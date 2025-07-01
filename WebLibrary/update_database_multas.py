#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para atualizar a base de dados com as novas tabelas do sistema de multas.
"""

import sqlite3
import os
from datetime import datetime

def get_db_path():
    """Retorna o caminho da base de dados"""
    return os.path.join('src', 'database', 'weblibrary.db')

def update_database():
    """Adicionar tabelas do sistema de multas à base de dados"""
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        print("❌ Base de dados não encontrada!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Atualizando base de dados com sistema de multas...")
        print("=" * 60)
        
        # 1. Tabela de multas por atraso
        cursor.execute('''CREATE TABLE IF NOT EXISTS multas (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         id_emprestimo INTEGER NOT NULL,
                         id_utilizador INTEGER NOT NULL,
                         valor_total DECIMAL(10,2) DEFAULT 0.00,
                         dias_atraso INTEGER DEFAULT 0,
                         data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                         data_pagamento TIMESTAMP,
                         status TEXT DEFAULT 'pendente' CHECK(status IN ('pendente', 'paga', 'cancelada')),
                         observacoes TEXT,
                         FOREIGN KEY (id_emprestimo) REFERENCES emprestimos (id),
                         FOREIGN KEY (id_utilizador) REFERENCES utilizadores (id)
                         )''')
        print("✅ Tabela 'multas' criada/verificada")

        # 2. Tabela de notificações de atraso
        cursor.execute('''CREATE TABLE IF NOT EXISTS notificacoes_atraso (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         id_emprestimo INTEGER NOT NULL,
                         id_utilizador INTEGER NOT NULL,
                         tipo_notificacao TEXT NOT NULL CHECK(tipo_notificacao IN ('email', 'sistema')),
                         conteudo TEXT NOT NULL,
                         data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                         email_enviado INTEGER DEFAULT 0,
                         dias_atraso INTEGER NOT NULL,
                         FOREIGN KEY (id_emprestimo) REFERENCES emprestimos (id),
                         FOREIGN KEY (id_utilizador) REFERENCES utilizadores (id)
                         )''')
        print("✅ Tabela 'notificacoes_atraso' criada/verificada")

        # 3. Tabela de histórico de multas (para auditoria)
        cursor.execute('''CREATE TABLE IF NOT EXISTS historico_multas (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         id_multa INTEGER NOT NULL,
                         acao TEXT NOT NULL CHECK(acao IN ('criada', 'atualizada', 'paga', 'cancelada')),
                         valor_anterior DECIMAL(10,2),
                         valor_novo DECIMAL(10,2),
                         usuario_acao INTEGER,
                         data_acao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                         observacoes TEXT,
                         FOREIGN KEY (id_multa) REFERENCES multas (id),
                         FOREIGN KEY (usuario_acao) REFERENCES utilizadores (id)
                         )''')
        print("✅ Tabela 'historico_multas' criada/verificada")

        # 4. Criar índices para melhor performance
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_multas_utilizador ON multas(id_utilizador)",
            "CREATE INDEX IF NOT EXISTS idx_multas_emprestimo ON multas(id_emprestimo)",
            "CREATE INDEX IF NOT EXISTS idx_multas_status ON multas(status)",
            "CREATE INDEX IF NOT EXISTS idx_notificacoes_emprestimo ON notificacoes_atraso(id_emprestimo)",
            "CREATE INDEX IF NOT EXISTS idx_historico_multa ON historico_multas(id_multa)"
        ]
        
        for idx_sql in indices:
            cursor.execute(idx_sql)
        
        print("✅ Índices criados/verificados")

        # 5. Verificar se existem empréstimos atrasados para criar multas de exemplo
        cursor.execute("""
            SELECT COUNT(*) FROM emprestimos 
            WHERE status = 'ativo' AND date(data_devolucao_prevista) < date('now')
        """)
        emprestimos_atrasados = cursor.fetchone()[0]
        
        print(f"\n📊 Estado atual da base de dados:")
        
        # Contar registros em cada tabela
        cursor.execute("SELECT COUNT(*) FROM multas")
        total_multas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM notificacoes_atraso")
        total_notificacoes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM historico_multas")
        total_historico = cursor.fetchone()[0]
        
        print(f"   💰 Multas: {total_multas}")
        print(f"   📧 Notificações: {total_notificacoes}")
        print(f"   📋 Histórico: {total_historico}")
        print(f"   ⚠️  Empréstimos atrasados: {emprestimos_atrasados}")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Base de dados atualizada com sucesso!")
        print(f"📁 Localização: {os.path.abspath(db_path)}")
        
        if emprestimos_atrasados > 0:
            print(f"\n💡 Para criar multas automáticas, execute:")
            print(f"   python -c \"from src.services.multas_service import executar_verificacao_atrasos; executar_verificacao_atrasos()\"")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar base de dados: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_sistema_multas():
    """Verificar se o sistema de multas está funcional"""
    print("\n🔍 Verificando sistema de multas...")
    print("=" * 50)
    
    try:
        # Importar e testar o serviço
        from src.services.multas_service import MultasService
        
        service = MultasService()
        print(f"✅ MultasService importado com sucesso")
        print(f"   Valor por dia: €{service.valor_multa_dia}")
        
        # Testar conexão com base de dados
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se as tabelas existem
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('multas', 'notificacoes_atraso', 'historico_multas')
        """)
        tabelas = [row[0] for row in cursor.fetchall()]
        
        tabelas_esperadas = ['multas', 'notificacoes_atraso', 'historico_multas']
        for tabela in tabelas_esperadas:
            if tabela in tabelas:
                print(f"✅ Tabela '{tabela}' existe")
            else:
                print(f"❌ Tabela '{tabela}' não encontrada")
        
        conn.close()
        print(f"\n✅ Sistema de multas verificado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Atualização do Sistema de Multas - WebLibrary")
    print("=" * 60)
    
    # 1. Atualizar base de dados
    if update_database():
        # 2. Verificar sistema
        verificar_sistema_multas()
        
        print(f"\n🎉 Atualização concluída com sucesso!")
        print(f"\n📝 Próximos passos:")
        print(f"   1. Iniciar a aplicação: cd src && python main.py")
        print(f"   2. Aceder a: http://localhost:5000/multas/admin/gestao")
        print(f"   3. Testar processamento: Botão 'Processar Atrasos'")
        
    else:
        print(f"\n❌ Falha na atualização!")

if __name__ == "__main__":
    main() 