#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço para processamento automático de multas e notificações de atraso.
"""

import sqlite3
import smtplib
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.models.database import get_db_connection

# Configurações de email (ajustar conforme necessário)
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email': 'biblioteca@escola.pt',  # Substituir pelo email real
    'password': 'sua_senha_aqui',     # Usar variáveis de ambiente em produção
    'nome_remetente': 'Biblioteca WebLibrary'
}

# Valor da multa por dia de atraso (em euros)
VALOR_MULTA_POR_DIA = 0.50

class MultasService:
    """Serviço para gestão de multas e notificações"""
    
    def __init__(self):
        self.valor_multa_dia = VALOR_MULTA_POR_DIA
    
    def processar_atrasos_diarios(self):
        """
        Função principal para processar atrasos diários.
        Deve ser executada uma vez por dia (via cron job ou task scheduler).
        """
        print(f"🔍 Verificando atrasos - {datetime.now()}")
        
        emprestimos_atrasados = self._obter_emprestimos_atrasados()
        
        if not emprestimos_atrasados:
            print("✅ Nenhum atraso encontrado.")
            return
        
        print(f"⚠️ {len(emprestimos_atrasados)} empréstimos atrasados")
        
        for emprestimo in emprestimos_atrasados:
            self._processar_emprestimo_atrasado(emprestimo)
    
    def _obter_emprestimos_atrasados(self):
        """Obter todos os empréstimos que estão atrasados"""
        with get_db_connection() as (conn, cursor):
            query = """
                SELECT e.*, u.nome, u.email, l.titulo, l.autor
                FROM emprestimos e
                JOIN utilizadores u ON e.id_utilizador = u.id
                JOIN livros l ON e.id_livro = l.id
                WHERE e.status = 'ativo' 
                AND date(e.data_devolucao_prevista) < date('now')
            """
            cursor.execute(query)
            return cursor.fetchall()
    
    def _processar_emprestimo_atrasado(self, emprestimo):
        """Processar um empréstimo específico atrasado"""
        try:
            # Calcular dias de atraso
            data_devolucao = datetime.strptime(emprestimo['data_devolucao_prevista'], '%Y-%m-%d %H:%M:%S')
            dias_atraso = (datetime.now() - data_devolucao).days
            
            print(f"📋 {emprestimo['titulo']} - {emprestimo['nome']} ({dias_atraso} dias)")
            
            # 1. Atualizar status do empréstimo para 'atrasado'
            self._atualizar_status_emprestimo(emprestimo['id'], 'atrasado')
            
            # 2. Verificar se já existe multa para este empréstimo
            multa_existente = self._obter_multa_emprestimo(emprestimo['id'])
            
            if multa_existente:
                # Atualizar multa existente
                self._atualizar_multa(multa_existente['id'], dias_atraso)
            else:
                # Criar nova multa
                self._criar_nova_multa(emprestimo, dias_atraso)
            
            # 3. Enviar notificação por email (uma vez por dia)
            if self._deve_enviar_notificacao(emprestimo['id'], dias_atraso):
                self._enviar_email_atraso(emprestimo, dias_atraso)
            
        except Exception as e:
            print(f"❌ Erro ao processar empréstimo {emprestimo['id']}: {e}")
    
    def _atualizar_status_emprestimo(self, emprestimo_id, status):
        """Atualizar o status de um empréstimo"""
        with get_db_connection() as (conn, cursor):
            cursor.execute("UPDATE emprestimos SET status = ? WHERE id = ?", (status, emprestimo_id))
            conn.commit()
    
    def _obter_multa_emprestimo(self, emprestimo_id):
        """Verificar se já existe multa para um empréstimo"""
        with get_db_connection() as (conn, cursor):
            cursor.execute("SELECT * FROM multas WHERE id_emprestimo = ? AND status = 'pendente'", (emprestimo_id,))
            return cursor.fetchone()
    
    def _criar_nova_multa(self, emprestimo, dias_atraso):
        """Criar uma nova multa"""
        valor_total = dias_atraso * self.valor_multa_dia
        
        with get_db_connection() as (conn, cursor):
            cursor.execute("""
                INSERT INTO multas (id_emprestimo, id_utilizador, valor_total, dias_atraso, status)
                VALUES (?, ?, ?, ?, 'pendente')
            """, (emprestimo['id'], emprestimo['id_utilizador'], valor_total, dias_atraso))
            
            multa_id = cursor.lastrowid
            
            # Registrar no histórico
            cursor.execute("""
                INSERT INTO historico_multas (id_multa, acao, valor_novo, observacoes)
                VALUES (?, 'criada', ?, ?)
            """, (multa_id, valor_total, f"Criada por {dias_atraso} dias de atraso"))
            
            conn.commit()
            print(f"  💰 Multa criada: €{valor_total:.2f}")
    
    def _atualizar_multa(self, multa_id, dias_atraso):
        """Atualizar uma multa existente"""
        novo_valor = dias_atraso * self.valor_multa_dia
        
        with get_db_connection() as (conn, cursor):
            # Obter valor anterior
            cursor.execute("SELECT valor_total FROM multas WHERE id = ?", (multa_id,))
            valor_anterior = cursor.fetchone()['valor_total']
            
            # Atualizar multa
            cursor.execute("""
                UPDATE multas SET valor_total = ?, dias_atraso = ?
                WHERE id = ?
            """, (novo_valor, dias_atraso, multa_id))
            
            # Registrar no histórico
            cursor.execute("""
                INSERT INTO historico_multas (id_multa, acao, valor_anterior, valor_novo, observacoes)
                VALUES (?, 'atualizada', ?, ?, ?)
            """, (multa_id, valor_anterior, novo_valor, f"Atualizada para {dias_atraso} dias de atraso"))
            
            conn.commit()
            print(f"  💰 Multa atualizada: €{valor_anterior:.2f} → €{novo_valor:.2f}")
    
    def _deve_enviar_notificacao(self, emprestimo_id, dias_atraso):
        """Verificar se deve enviar notificação (uma vez por dia)"""
        with get_db_connection() as (conn, cursor):
            # Verificar se já foi enviada notificação hoje
            cursor.execute("""
                SELECT COUNT(*) FROM notificacoes_atraso 
                WHERE id_emprestimo = ? 
                AND date(data_envio) = date('now')
                AND dias_atraso = ?
            """, (emprestimo_id, dias_atraso))
            
            return cursor.fetchone()[0] == 0
    
    def _enviar_email_atraso(self, emprestimo, dias_atraso):
        """Enviar email de notificação de atraso"""
        try:
            # Verificar se o utilizador tem notificações ativas
            with get_db_connection() as (conn, cursor):
                cursor.execute(
                    "SELECT notificacoes_email FROM utilizadores WHERE id = ?",
                    (emprestimo['id_utilizador'],)
                )
                notificacoes_ativas = cursor.fetchone()['notificacoes_email']
                
                if not notificacoes_ativas:
                    print(f"  📧 Notificações desativadas para {emprestimo['nome']}")
                    return
            
            # Calcular valor da multa
            valor_multa = dias_atraso * self.valor_multa_dia
            
            # Criar conteúdo do email
            assunto = f"⚠️ Livro em Atraso - Multa de €{valor_multa:.2f}"
            
            conteudo_html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h2 style="color: #dc3545; margin: 0;">📚 Livro em Atraso</h2>
                    </div>
                    
                    <p>Caro(a) <strong>{emprestimo['nome']}</strong>,</p>
                    
                    <p>Informamos que o seguinte livro está em atraso:</p>
                    
                    <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="margin: 0;"><strong>📖 Livro:</strong> {emprestimo['titulo']}</p>
                        <p style="margin: 5px 0;"><strong>✍️ Autor:</strong> {emprestimo['autor']}</p>
                        <p style="margin: 5px 0;"><strong>📅 Data prevista:</strong> {datetime.strptime(emprestimo['data_devolucao_prevista'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')}</p>
                        <p style="margin: 5px 0;"><strong>⏰ Dias de atraso:</strong> {dias_atraso} dias</p>
                        <p style="margin: 5px 0;"><strong>💰 Multa acumulada:</strong> €{valor_multa:.2f}</p>
                    </div>
                    
                    <div style="background: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #0c5460;">💡 Informações Importantes:</h3>
                        <ul style="margin: 10px 0; padding-left: 20px;">
                            <li>A multa é de <strong>€0.50 por dia de atraso</strong></li>
                            <li>A multa continua a acumular até à devolução do livro</li>
                            <li>Devolva o livro o mais rapidamente possível</li>
                            <li>Em caso de dificuldades, contacte a biblioteca</li>
                        </ul>
                    </div>
                    
                    <p style="text-align: center; margin: 30px 0;">
                        <a href="http://localhost:5000/loans/view" style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            📋 Ver Meus Empréstimos
                        </a>
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    
                    <p style="font-size: 12px; color: #666; text-align: center;">
                        Esta é uma mensagem automática da <strong>WebLibrary</strong><br>
                        Para deixar de receber estas notificações, aceda às definições da sua conta.
                    </p>
                </div>
            </body>
            </html>
            """
            
            # Enviar email (simulação - em produção configurar SMTP real)
            email_enviado = self._simular_envio_email(emprestimo['email'], assunto, conteudo_html)
            
            # Registrar notificação na base de dados
            self._registrar_notificacao(emprestimo, dias_atraso, conteudo_html, email_enviado)
            
            if email_enviado:
                print(f"  📧 Email enviado para {emprestimo['email']}")
            else:
                print(f"  ⚠️  Falha ao enviar email para {emprestimo['email']}")
                
        except Exception as e:
            print(f"❌ Erro ao enviar email: {e}")
    
    def _simular_envio_email(self, destinatario, assunto, conteudo):
        """
        Simular envio de email (para desenvolvimento).
        Em produção, implementar envio real via SMTP.
        """
        print(f"  📧 [SIMULAÇÃO] Email para: {destinatario}")
        print(f"     Assunto: {assunto}")
        
        # Guardar email em ficheiro para desenvolvimento
        try:
            os.makedirs('logs/emails', exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"logs/emails/atraso_{timestamp}_{destinatario.replace('@', '_')}.html"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"<h1>Email: {assunto}</h1>\n")
                f.write(f"<p><strong>Para:</strong> {destinatario}</p>\n")
                f.write(f"<p><strong>Data:</strong> {datetime.now()}</p>\n")
                f.write("<hr>\n")
                f.write(conteudo)
            
            print(f"     💾 Email guardado em: {filename}")
            return True
            
        except Exception as e:
            print(f"     ❌ Erro ao guardar email: {e}")
            return False
    
    def _registrar_notificacao(self, emprestimo, dias_atraso, conteudo, email_enviado):
        """Registrar notificação na base de dados"""
        with get_db_connection() as (conn, cursor):
            cursor.execute("""
                INSERT INTO notificacoes_atraso 
                (id_emprestimo, id_utilizador, tipo_notificacao, conteudo, email_enviado, dias_atraso)
                VALUES (?, ?, 'email', ?, ?, ?)
            """, (emprestimo['id'], emprestimo['id_utilizador'], conteudo, email_enviado, dias_atraso))
            conn.commit()
    
    def obter_multas_utilizador(self, user_id):
        """Obter todas as multas de um utilizador"""
        with get_db_connection() as (conn, cursor):
            query = """
                SELECT m.*, e.data_emprestimo, e.data_devolucao_prevista, 
                       l.titulo, l.autor
                FROM multas m
                JOIN emprestimos e ON m.id_emprestimo = e.id
                JOIN livros l ON e.id_livro = l.id
                WHERE m.id_utilizador = ?
                ORDER BY m.data_criacao DESC
            """
            cursor.execute(query, (user_id,))
            return cursor.fetchall()
    
    def obter_multas_pendentes(self):
        """Obter todas as multas pendentes (para admins)"""
        with get_db_connection() as (conn, cursor):
            query = """
                SELECT m.*, u.nome, u.email, l.titulo, l.autor,
                       e.data_emprestimo, e.data_devolucao_prevista
                FROM multas m
                JOIN utilizadores u ON m.id_utilizador = u.id
                JOIN emprestimos e ON m.id_emprestimo = e.id
                JOIN livros l ON e.id_livro = l.id
                WHERE m.status = 'pendente'
                ORDER BY m.valor_total DESC, m.data_criacao
            """
            cursor.execute(query)
            return cursor.fetchall()
    
    def pagar_multa(self, multa_id, admin_id=None):
        """Marcar uma multa como paga"""
        with get_db_connection() as (conn, cursor):
            # Obter valor da multa
            cursor.execute("SELECT valor_total FROM multas WHERE id = ?", (multa_id,))
            resultado = cursor.fetchone()
            
            if not resultado:
                return False
            
            valor = resultado['valor_total']
            
            # Atualizar multa
            cursor.execute("""
                UPDATE multas SET status = 'paga', data_pagamento = ?
                WHERE id = ?
            """, (datetime.now(), multa_id))
            
            # Registrar no histórico
            cursor.execute("""
                INSERT INTO historico_multas (id_multa, acao, valor_novo, usuario_acao, observacoes)
                VALUES (?, 'paga', ?, ?, ?)
            """, (multa_id, valor, admin_id, f"Multa paga no valor de €{valor:.2f}"))
            
            conn.commit()
            return True

# Função principal para execução agendada
def executar_verificacao_atrasos():
    """Função principal para ser executada diariamente"""
    service = MultasService()
    service.processar_atrasos_diarios()

if __name__ == "__main__":
    # Para testes - executar verificação imediatamente
    executar_verificacao_atrasos() 