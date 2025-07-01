from flask import Blueprint, render_template, session, redirect, url_for
from src.models.database import get_db_connection

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage - redireciona para dashboard se logado, senão mostra página inicial"""
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    
    # Estatísticas para a homepage
    with get_db_connection() as (conn, cursor):
        cursor.execute("SELECT COUNT(*) FROM livros")
        total_livros = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM utilizadores WHERE tipo != 'admin'")
        total_utilizadores = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT categoria) FROM livros")
        total_categorias = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM emprestimos")
        total_emprestimos = cursor.fetchone()[0]
    
    stats = {
        'livros': total_livros,
        'utilizadores': total_utilizadores,
        'categorias': total_categorias,
        'emprestimos': total_emprestimos
    }
    
    return render_template('main/index.html', stats=stats)

@main_bp.route('/dashboard')
def dashboard():
    """Dashboard baseado no tipo de utilizador"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_type = session.get('user_type')
    user_id = session.get('user_id')
    
    with get_db_connection() as (conn, cursor):
        if user_type == 'admin':
            # Estatísticas para admin
            cursor.execute("SELECT COUNT(*) FROM livros")
            total_livros = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM livros WHERE status = 'disponivel'")
            livros_disponiveis = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM utilizadores")
            total_utilizadores = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM emprestimos WHERE status = 'ativo'")
            emprestimos_ativos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM emprestimos WHERE status = 'atrasado'")
            emprestimos_atrasados = cursor.fetchone()[0]
            
            # Empréstimos recentes
            cursor.execute("""SELECT e.*, l.titulo, l.autor, u.nome as nome_utilizador
                             FROM emprestimos e 
                             JOIN livros l ON e.id_livro = l.id 
                             JOIN utilizadores u ON e.id_utilizador = u.id
                             ORDER BY e.data_emprestimo DESC LIMIT 5""")
            emprestimos_recentes = cursor.fetchall()
            
            # Dados para "Requisições por Mês" (últimos 6 meses)
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN strftime('%m', data_emprestimo) = '01' THEN 'Jan'
                        WHEN strftime('%m', data_emprestimo) = '02' THEN 'Fev'
                        WHEN strftime('%m', data_emprestimo) = '03' THEN 'Mar'
                        WHEN strftime('%m', data_emprestimo) = '04' THEN 'Abr'
                        WHEN strftime('%m', data_emprestimo) = '05' THEN 'Mai'
                        WHEN strftime('%m', data_emprestimo) = '06' THEN 'Jun'
                        WHEN strftime('%m', data_emprestimo) = '07' THEN 'Jul'
                        WHEN strftime('%m', data_emprestimo) = '08' THEN 'Ago'
                        WHEN strftime('%m', data_emprestimo) = '09' THEN 'Set'
                        WHEN strftime('%m', data_emprestimo) = '10' THEN 'Out'
                        WHEN strftime('%m', data_emprestimo) = '11' THEN 'Nov'
                        WHEN strftime('%m', data_emprestimo) = '12' THEN 'Dez'
                        ELSE strftime('%m', data_emprestimo)
                    END as mes,
                    COUNT(*) as total
                FROM emprestimos 
                WHERE data_emprestimo >= date('now', '-6 months')
                GROUP BY strftime('%Y-%m', data_emprestimo)
                ORDER BY strftime('%Y-%m', data_emprestimo)
                LIMIT 6
            """)
            monthly_data_raw = cursor.fetchall()
            
            # Converter para formato do template
            monthly_data = []
            for row in monthly_data_raw:
                monthly_data.append({
                    'label': row[0],
                    'value': row[1]
                })
            
            # Se não há dados, criar estrutura vazia mas válida
            if len(monthly_data) == 0:
                import datetime
                months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                current_month = datetime.datetime.now().month
                
                for i in range(6):
                    month_idx = (current_month - (6 - i)) % 12
                    month_name = months[month_idx] if month_idx >= 0 else months[month_idx + 12]
                    monthly_data.append({'label': month_name, 'value': 0})
            
            # Se não há dados suficientes, preencher com zeros
            elif len(monthly_data) < 6:
                months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                import datetime
                current_month = datetime.datetime.now().month
                
                # Completar os dados em falta
                for i in range(6 - len(monthly_data)):
                    month_idx = (current_month - (6 - i - 1)) % 12
                    month_name = months[month_idx - 1] if month_idx > 0 else months[11]
                    
                    # Verificar se o mês já existe nos dados
                    if not any(data['label'] == month_name for data in monthly_data):
                        monthly_data.insert(i, {'label': month_name, 'value': 0})
            
            # Atividade Recente - últimas ações no sistema
            atividade_recente = []
            
            # Últimos empréstimos
            cursor.execute("""
                SELECT 'emprestimo' as tipo, e.data_emprestimo as data, 
                       l.titulo, u.nome, e.id
                FROM emprestimos e
                JOIN livros l ON e.id_livro = l.id
                JOIN utilizadores u ON e.id_utilizador = u.id
                ORDER BY e.data_emprestimo DESC
                LIMIT 3
            """)
            emprestimos_recentes_atividade = cursor.fetchall()
            
            for row in emprestimos_recentes_atividade:
                atividade_recente.append({
                    'tipo': 'emprestimo',
                    'data': row[1],
                    'titulo': row[2],
                    'usuario': row[3],
                    'id': row[4]
                })
            
            # Últimas devoluções
            cursor.execute("""
                SELECT 'devolucao' as tipo, e.data_devolucao_real as data,
                       l.titulo, u.nome, e.id
                FROM emprestimos e
                JOIN livros l ON e.id_livro = l.id
                JOIN utilizadores u ON e.id_utilizador = u.id
                WHERE e.status = 'devolvido' AND e.data_devolucao_real IS NOT NULL
                ORDER BY e.data_devolucao_real DESC
                LIMIT 2
            """)
            devolucoes_recentes = cursor.fetchall()
            
            for row in devolucoes_recentes:
                atividade_recente.append({
                    'tipo': 'devolucao',
                    'data': row[1],
                    'titulo': row[2],
                    'usuario': row[3],
                    'id': row[4]
                })
            
            # Últimos livros adicionados
            cursor.execute("""
                SELECT 'livro_adicionado' as tipo, data_adicao as data,
                       titulo, autor, id
                FROM livros
                WHERE data_adicao IS NOT NULL
                ORDER BY data_adicao DESC
                LIMIT 2
            """)
            livros_novos = cursor.fetchall()
            
            for row in livros_novos:
                atividade_recente.append({
                    'tipo': 'livro_adicionado',
                    'data': row[1],
                    'titulo': row[2],
                    'usuario': row[3],  # autor neste caso
                    'id': row[4]
                })
            
            # Últimos utilizadores registados
            cursor.execute("""
                SELECT 'usuario_registado' as tipo, data_criacao as data,
                       nome, email, id
                FROM utilizadores
                WHERE data_criacao IS NOT NULL AND tipo != 'admin'
                ORDER BY data_criacao DESC
                LIMIT 2
            """)
            usuarios_novos = cursor.fetchall()
            
            for row in usuarios_novos:
                atividade_recente.append({
                    'tipo': 'usuario_registado',
                    'data': row[1],
                    'titulo': row[2],  # nome neste caso
                    'usuario': row[3],  # email neste caso
                    'id': row[4]
                })
            
            # Ordenar por data e pegar apenas os 5 mais recentes
            atividade_recente = sorted(atividade_recente, 
                                     key=lambda x: x['data'] if x['data'] else '1970-01-01', 
                                     reverse=True)[:5]
            
            # Garantir que atividade_recente nunca seja None
            if not atividade_recente:
                atividade_recente = []
            
            return render_template('dashboard/admin.html',
                                 total_livros=total_livros,
                                 livros_disponiveis=livros_disponiveis,
                                 total_utilizadores=total_utilizadores,
                                 emprestimos_ativos=emprestimos_ativos,
                                 emprestimos_atrasados=emprestimos_atrasados,
                                 emprestimos_recentes=emprestimos_recentes,
                                 monthly_data=monthly_data,
                                 atividade_recente=atividade_recente)
        
        else:
            # Dashboard para alunos/professores
            # Empréstimos ativos do utilizador
            cursor.execute("""SELECT e.*, l.titulo, l.autor, l.capa_url 
                             FROM emprestimos e 
                             JOIN livros l ON e.id_livro = l.id 
                             WHERE e.id_utilizador = ? AND e.status = 'ativo'
                             ORDER BY e.data_emprestimo DESC""", (user_id,))
            emprestimos_ativos = cursor.fetchall()
            
            # Livros recentemente adicionados
            cursor.execute("""SELECT * FROM livros WHERE status = 'disponivel' 
                             ORDER BY data_adicao DESC LIMIT 6""")
            livros_recentes = cursor.fetchall()
            
            # Estatísticas pessoais
            cursor.execute("SELECT COUNT(*) FROM emprestimos WHERE id_utilizador = ?", (user_id,))
            total_emprestimos = cursor.fetchone()[0]
            
            cursor.execute("""SELECT COUNT(*) FROM emprestimos 
                             WHERE id_utilizador = ? AND status = 'devolvido'""", (user_id,))
            emprestimos_devolvidos = cursor.fetchone()[0]
            
            # Categorias favoritas
            cursor.execute("""SELECT l.categoria, COUNT(*) as count
                             FROM emprestimos e
                             JOIN livros l ON e.id_livro = l.id
                             WHERE e.id_utilizador = ?
                             GROUP BY l.categoria
                             ORDER BY count DESC
                             LIMIT 3""", (user_id,))
            categorias_favoritas = cursor.fetchall()
            
            return render_template('dashboard/user.html',
                                 emprestimos_ativos=emprestimos_ativos,
                                 livros_recentes=livros_recentes,
                                 total_emprestimos=total_emprestimos,
                                 emprestimos_devolvidos=emprestimos_devolvidos,
                                 categorias_favoritas=categorias_favoritas)

