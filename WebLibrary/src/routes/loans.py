from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from src.models.database import get_db_connection
from datetime import datetime, timedelta

loans_bp = Blueprint('loans', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@loans_bp.route('/emprestimos')
@login_required
def view_loans():
    """Visualizar empréstimos (todos para admin, próprios para utilizadores)"""
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    
    # Filtros
    status_filter = request.args.get('status', '')
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    utilizador_filter = request.args.get('utilizador', '')
    
    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Número de registros por página
    offset = (page - 1) * per_page
    
    with get_db_connection() as (conn, cursor):
        # Construir query base e parâmetros
        if user_type == 'admin':
            # Admin vê todos os empréstimos
            base_query = """FROM emprestimos e 
                           JOIN livros l ON e.id_livro = l.id 
                           JOIN utilizadores u ON e.id_utilizador = u.id
                           WHERE 1=1"""
            params = []
            
            if status_filter:
                base_query += " AND e.status = ?"
                params.append(status_filter)
            
            if data_inicio:
                base_query += " AND date(e.data_emprestimo) >= ?"
                params.append(data_inicio)
            
            if data_fim:
                base_query += " AND date(e.data_emprestimo) <= ?"
                params.append(data_fim)
            
            if utilizador_filter:
                base_query += " AND u.nome LIKE ?"
                params.append(f"%{utilizador_filter}%")
            
            # Contar total de registros
            count_query = "SELECT COUNT(*) " + base_query
            cursor.execute(count_query, params)
            total_records = cursor.fetchone()[0]
            
            # Buscar registros com paginação
            data_query = """SELECT e.id, e.id_utilizador, e.id_livro, e.data_emprestimo, e.data_devolucao_prevista, 
                                   e.data_devolucao_real, e.status, e.renovado,
                                   l.titulo, l.autor, l.capa_url, u.nome as nome_utilizador, u.email as email_utilizador,
                                   CAST(julianday(e.data_devolucao_prevista) - julianday('now') AS INTEGER) as dias_restantes
                            """ + base_query + " ORDER BY e.data_emprestimo DESC LIMIT ? OFFSET ?"
            cursor.execute(data_query, params + [per_page, offset])
            emprestimos_raw = cursor.fetchall()
            
            # 🔧 VALIDAÇÃO: Filtrar empréstimos com ID NULL e converter para dict
            emprestimos = []
            for emp in emprestimos_raw:
                if emp['id'] is not None:  # Só incluir empréstimos com ID válido
                    emprestimos.append(dict(emp))
                else:
                    print(f"⚠️ Empréstimo com ID NULL ignorado: {emp['titulo']} - {emp['nome_utilizador']}")
            
        else:
            # Utilizadores veem apenas os seus empréstimos
            base_query = """FROM emprestimos e 
                           JOIN livros l ON e.id_livro = l.id 
                           WHERE e.id_utilizador = ?"""
            params = [user_id]
            
            if status_filter:
                base_query += " AND e.status = ?"
                params.append(status_filter)
            
            if data_inicio:
                base_query += " AND date(e.data_emprestimo) >= ?"
                params.append(data_inicio)
            
            if data_fim:
                base_query += " AND date(e.data_emprestimo) <= ?"
                params.append(data_fim)
            
            # Contar total de registros
            count_query = "SELECT COUNT(*) " + base_query
            cursor.execute(count_query, params)
            total_records = cursor.fetchone()[0]
            
            # Buscar registros com paginação
            data_query = """SELECT e.id, e.id_utilizador, e.id_livro, e.data_emprestimo, e.data_devolucao_prevista, 
                                   e.data_devolucao_real, e.status, e.renovado,
                                   l.titulo, l.autor, l.capa_url,
                                   CAST(julianday(e.data_devolucao_prevista) - julianday('now') AS INTEGER) as dias_restantes
                            """ + base_query + " ORDER BY e.data_emprestimo DESC LIMIT ? OFFSET ?"
            cursor.execute(data_query, params + [per_page, offset])
            emprestimos_raw = cursor.fetchall()
            
            # 🔧 VALIDAÇÃO: Filtrar empréstimos com ID NULL e converter para dict
            emprestimos = []
            for emp in emprestimos_raw:
                if emp['id'] is not None:  # Só incluir empréstimos com ID válido
                    emprestimos.append(dict(emp))
                else:
                    print(f"⚠️ Empréstimo com ID NULL ignorado: {emp['titulo']}")
        
        # Calcular informações de paginação
        total_pages = (total_records + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        prev_page = page - 1 if has_prev else None
        next_page = page + 1 if has_next else None
        
        # Gerar números de página para navegação
        page_numbers = []
        start_page = max(1, page - 2)
        end_page = min(total_pages, page + 2)
        
        if start_page > 1:
            page_numbers.append(1)
            if start_page > 2:
                page_numbers.append('...')
        
        for p in range(start_page, end_page + 1):
            page_numbers.append(p)
        
        if end_page < total_pages:
            if end_page < total_pages - 1:
                page_numbers.append('...')
            page_numbers.append(total_pages)
        
        # Get statistics for the dashboard
        if user_type == 'admin':
            cursor.execute("SELECT COUNT(*) FROM emprestimos WHERE status = 'ativo'")
            stats_ativos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM emprestimos WHERE status = 'devolvido'")
            stats_devolvidos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM emprestimos WHERE status = 'atrasado'")
            stats_atrasados = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM emprestimos")
            stats_total = cursor.fetchone()[0]
        else:
            cursor.execute("SELECT COUNT(*) FROM emprestimos WHERE id_utilizador = ? AND status = 'ativo'", (user_id,))
            stats_ativos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM emprestimos WHERE id_utilizador = ? AND status = 'devolvido'", (user_id,))
            stats_devolvidos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM emprestimos WHERE id_utilizador = ? AND status = 'atrasado'", (user_id,))
            stats_atrasados = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM emprestimos WHERE id_utilizador = ?", (user_id,))
            stats_total = cursor.fetchone()[0]
        
        stats = {
            'ativos': stats_ativos,
            'devolvidos': stats_devolvidos,
            'atrasados': stats_atrasados,
            'total': stats_total
        }
        
        # Função helper para construir URLs de paginação
        def build_url(page_num):
            args = request.args.copy()
            args['page'] = page_num
            return url_for('loans.view_loans', **args)
    
    return render_template('loans/view_loans.html', 
                         emprestimos=emprestimos, 
                         status_filter=status_filter,
                         data_inicio=data_inicio,
                         data_fim=data_fim,
                         utilizador=utilizador_filter,
                         user_type=user_type,
                         stats=stats,
                         # Variáveis de paginação
                         page=page,
                         total_pages=total_pages,
                         total_records=total_records,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_page=prev_page,
                         next_page=next_page,
                         page_numbers=page_numbers,
                         build_url=build_url)

@loans_bp.route('/emprestimos/solicitar/<int:livro_id>', methods=['GET', 'POST'])
@login_required
def request_loan(livro_id):
    """Solicitar empréstimo de um livro"""
    user_id = session.get('user_id')
    
    with get_db_connection() as (conn, cursor):
        # Verificar se o livro existe
        cursor.execute("SELECT * FROM livros WHERE id = ?", (livro_id,))
        livro = cursor.fetchone()
        
        if not livro:
            flash('Livro não encontrado.', 'error')
            return redirect(url_for('books.catalog'))
        
        # Verificar se o livro está disponível
        if livro['status'] != 'disponivel':
            flash('Livro não disponível para empréstimo.', 'error')
            return redirect(url_for('books.details', livro_id=livro_id))
        
        # Verificar limite de empréstimos (máximo 3)
        cursor.execute("""SELECT COUNT(*) FROM emprestimos 
                         WHERE id_utilizador = ? AND status = 'ativo'""", (user_id,))
        active_loans = cursor.fetchone()[0]
        
        if active_loans >= 3:
            flash('Limite máximo de 3 empréstimos atingido. Devolva um livro antes de emprestar outro.', 'error')
            return redirect(url_for('books.details', livro_id=livro_id))
        
        # Verificar se já tem este livro emprestado
        cursor.execute("""SELECT COUNT(*) FROM emprestimos 
                         WHERE id_utilizador = ? AND id_livro = ? AND status = 'ativo'""", 
                      (user_id, livro_id))
        already_borrowed = cursor.fetchone()[0]
        
        if already_borrowed > 0:
            flash('Já tem este livro emprestado.', 'error')
            return redirect(url_for('books.details', livro_id=livro_id))
        
        # Se é uma requisição GET, mostrar o formulário
        if request.method == 'GET':
            # Obter dados do usuário
            cursor.execute("SELECT email FROM utilizadores WHERE id = ?", (user_id,))
            user_data = cursor.fetchone()
            
            # Obter histórico de empréstimos do usuário
            cursor.execute("""SELECT e.*, l.titulo as titulo_livro
                             FROM emprestimos e
                             JOIN livros l ON e.id_livro = l.id
                             WHERE e.id_utilizador = ?
                             ORDER BY e.data_emprestimo DESC
                             LIMIT 5""", (user_id,))
            emprestimos_data = cursor.fetchall()
            
            # Converter strings de data para objetos datetime
            emprestimos_utilizador = []
            for emprestimo in emprestimos_data:
                emprestimo_dict = dict(emprestimo)
                
                # Converter data_emprestimo
                if emprestimo_dict.get('data_emprestimo'):
                    try:
                        emprestimo_dict['data_emprestimo'] = datetime.strptime(emprestimo_dict['data_emprestimo'], '%Y-%m-%d %H:%M:%S')
                    except (ValueError, TypeError):
                        emprestimo_dict['data_emprestimo'] = None
                
                # Converter data_devolucao_real
                if emprestimo_dict.get('data_devolucao_real'):
                    try:
                        emprestimo_dict['data_devolucao_real'] = datetime.strptime(emprestimo_dict['data_devolucao_real'], '%Y-%m-%d %H:%M:%S')
                    except (ValueError, TypeError):
                        emprestimo_dict['data_devolucao_real'] = None
                
                # Converter data_devolucao_prevista
                if emprestimo_dict.get('data_devolucao_prevista'):
                    try:
                        emprestimo_dict['data_devolucao_prevista'] = datetime.strptime(emprestimo_dict['data_devolucao_prevista'], '%Y-%m-%d %H:%M:%S')
                    except (ValueError, TypeError):
                        emprestimo_dict['data_devolucao_prevista'] = None
                
                emprestimos_utilizador.append(emprestimo_dict)
            
            # Preparar dados para o template
            hoje = datetime.now()
            data_devolucao_prevista = hoje + timedelta(days=15)
            
            return render_template('loans/request_loan.html',
                                 livro=livro,
                                 emprestimos_utilizador=emprestimos_utilizador,
                                 today=hoje.strftime('%Y-%m-%d'),
                                 data_devolucao_prevista=data_devolucao_prevista.strftime('%Y-%m-%d'),
                                 user_email=user_data['email'] if user_data else '')
        
        # Se é uma requisição POST, processar o empréstimo
        if request.method == 'POST':
            # Criar empréstimo
            data_emprestimo = datetime.now()
            data_devolucao_prevista = data_emprestimo + timedelta(days=15)  # 15 dias de prazo
            
            try:
                cursor.execute("""INSERT INTO emprestimos 
                                 (id_utilizador, id_livro, data_emprestimo, data_devolucao_prevista, status) 
                                 VALUES (?, ?, ?, ?, 'ativo')""",
                              (user_id, livro_id, data_emprestimo, data_devolucao_prevista))
                
                # Atualizar status do livro
                cursor.execute("UPDATE livros SET status = 'emprestado' WHERE id = ?", (livro_id,))
                
                conn.commit()
                flash(f'Empréstimo do livro "{livro["titulo"]}" realizado com sucesso! Prazo de devolução: {data_devolucao_prevista.strftime("%d/%m/%Y")}.', 'success')
                
            except Exception as e:
                flash('Erro ao processar empréstimo. Tente novamente.', 'error')
        
        return redirect(url_for('books.details', livro_id=livro_id))

@loans_bp.route('/emprestimos/<int:emprestimo_id>/devolver', methods=['POST'])
@login_required
def return_loan(emprestimo_id):
    """Devolver um livro emprestado"""
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    
    with get_db_connection() as (conn, cursor):
        # Verificar se o empréstimo existe e pertence ao utilizador (ou se é admin)
        if user_type == 'admin':
            cursor.execute("SELECT * FROM emprestimos WHERE id = ? AND status = 'ativo'", (emprestimo_id,))
        else:
            cursor.execute("""SELECT * FROM emprestimos 
                             WHERE id = ? AND id_utilizador = ? AND status = 'ativo'""", 
                          (emprestimo_id, user_id))
        
        emprestimo = cursor.fetchone()
        
        if not emprestimo:
            flash('Empréstimo não encontrado ou já devolvido.', 'error')
            return redirect(url_for('loans.view_loans'))
        
        try:
            # Atualizar empréstimo
            data_devolucao_real = datetime.now()
            cursor.execute("""UPDATE emprestimos 
                             SET status = 'devolvido', data_devolucao_real = ? 
                             WHERE id = ?""",
                          (data_devolucao_real, emprestimo_id))
            
            # Atualizar status do livro
            cursor.execute("UPDATE livros SET status = 'disponivel' WHERE id = ?", 
                          (emprestimo['id_livro'],))
            
            conn.commit()
            flash('Livro devolvido com sucesso!', 'success')
            
        except Exception as e:
            flash('Erro ao processar devolução. Tente novamente.', 'error')
    
    return redirect(url_for('loans.view_loans'))

@loans_bp.route('/emprestimos/<int:emprestimo_id>/renovar', methods=['POST'])
@login_required
def renew_loan(emprestimo_id):
    """Renovar um empréstimo"""
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    
    with get_db_connection() as (conn, cursor):
        # Verificar se o empréstimo existe e pertence ao utilizador (ou se é admin)
        if user_type == 'admin':
            cursor.execute("SELECT * FROM emprestimos WHERE id = ? AND status = 'ativo'", (emprestimo_id,))
        else:
            cursor.execute("""SELECT * FROM emprestimos 
                             WHERE id = ? AND id_utilizador = ? AND status = 'ativo'""", 
                          (emprestimo_id, user_id))
        
        emprestimo = cursor.fetchone()
        
        if not emprestimo:
            flash('Empréstimo não encontrado ou já devolvido.', 'error')
            return redirect(url_for('loans.view_loans'))
        
        # Verificar se já foi renovado
        if emprestimo['renovado']:
            flash('Este empréstimo já foi renovado. Não é possível renovar novamente.', 'error')
            return redirect(url_for('loans.view_loans'))
        
        try:
            # Estender prazo por mais 15 dias
            data_devolucao_atual = datetime.fromisoformat(emprestimo['data_devolucao_prevista'])
            nova_data_devolucao = data_devolucao_atual + timedelta(days=15)
            
            cursor.execute("""UPDATE emprestimos 
                             SET data_devolucao_prevista = ?, renovado = 1 
                             WHERE id = ?""",
                          (nova_data_devolucao, emprestimo_id))
            
            conn.commit()
            flash(f'Empréstimo renovado com sucesso! Nova data de devolução: {nova_data_devolucao.strftime("%d/%m/%Y")}.', 'success')
            
        except Exception as e:
            flash('Erro ao renovar empréstimo. Tente novamente.', 'error')
    
    return redirect(url_for('loans.view_loans'))

@loans_bp.route('/emprestimos/<int:emprestimo_id>/detalhes')
@login_required
def loan_details(emprestimo_id):
    """Exibir detalhes completos de um empréstimo"""
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    
    with get_db_connection() as (conn, cursor):
        # Query base para obter dados do empréstimo
        if user_type == 'admin':
            # Admin pode ver qualquer empréstimo
            cursor.execute("""
                SELECT e.*, l.titulo, l.autor, l.categoria, l.isbn, l.editora, l.ano_publicacao,
                       l.paginas, l.idioma, l.descricao as livro_descricao, l.capa_url,
                       u.nome as nome_utilizador, u.email as email_utilizador,
                       CAST(julianday(e.data_devolucao_prevista) - julianday('now') AS INTEGER) as dias_restantes
                FROM emprestimos e 
                JOIN livros l ON e.id_livro = l.id 
                JOIN utilizadores u ON e.id_utilizador = u.id
                WHERE e.id = ?
            """, (emprestimo_id,))
        else:
            # Utilizadores comuns só veem os próprios empréstimos
            cursor.execute("""
                SELECT e.*, l.titulo, l.autor, l.categoria, l.isbn, l.editora, l.ano_publicacao,
                       l.paginas, l.idioma, l.descricao as livro_descricao, l.capa_url,
                       u.nome as nome_utilizador, u.email as email_utilizador,
                       CAST(julianday(e.data_devolucao_prevista) - julianday('now') AS INTEGER) as dias_restantes
                FROM emprestimos e 
                JOIN livros l ON e.id_livro = l.id 
                JOIN utilizadores u ON e.id_utilizador = u.id
                WHERE e.id = ? AND e.id_utilizador = ?
            """, (emprestimo_id, user_id))
        
        emprestimo_data = cursor.fetchone()
        
        if not emprestimo_data:
            flash('Empréstimo não encontrado ou acesso negado.', 'error')
            return redirect(url_for('loans.view_loans'))
        
        # Converter dados para dicionário e ajustar datas
        emprestimo = dict(emprestimo_data)
        
        # Converter strings de data para objetos datetime
        date_fields = ['data_emprestimo', 'data_devolucao_prevista', 'data_devolucao_real']
        for field in date_fields:
            if emprestimo.get(field):
                try:
                    if isinstance(emprestimo[field], str):
                        emprestimo[field] = datetime.strptime(emprestimo[field], '%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    emprestimo[field] = None
        
        # Calcular informações adicionais
        emprestimo['status_info'] = {
            'ativo': {'label': 'Ativo', 'class': 'success', 'icon': 'fas fa-clock'},
            'devolvido': {'label': 'Devolvido', 'class': 'primary', 'icon': 'fas fa-check-circle'},
            'atrasado': {'label': 'Atrasado', 'class': 'danger', 'icon': 'fas fa-exclamation-triangle'}
        }.get(emprestimo['status'], {'label': 'Desconhecido', 'class': 'secondary', 'icon': 'fas fa-question'})
        
        # Calcular multa se houver atraso
        emprestimo['multa'] = 0
        if emprestimo['status'] == 'ativo' and emprestimo['dias_restantes'] < 0:
            dias_atraso = abs(emprestimo['dias_restantes'])
            emprestimo['multa'] = dias_atraso * 0.50  # €0.50 por dia
        
        # Inicializar listas vazias para histórico
        renovacoes = []
        historico_livro = []
        historico_utilizador = []
    
    return render_template('loans/loan_details.html',
                         emprestimo=emprestimo,
                         renovacoes=renovacoes,
                         historico_livro=historico_livro,
                         historico_utilizador=historico_utilizador,
                         user_type=user_type)

@loans_bp.route('/api/emprestimos/stats')
def loan_stats():
    """API para estatísticas de empréstimos"""
    with get_db_connection() as (conn, cursor):
        # Estatísticas mensais dos últimos 12 meses
        cursor.execute("""SELECT 
                            strftime('%Y-%m', data_emprestimo) as mes,
                            COUNT(*) as total_emprestimos
                         FROM emprestimos 
                         WHERE data_emprestimo >= date('now', '-12 months')
                         GROUP BY strftime('%Y-%m', data_emprestimo)
                         ORDER BY mes""")
        monthly_stats = cursor.fetchall()
        
        # Empréstimos em atraso
        cursor.execute("""SELECT COUNT(*) FROM emprestimos 
                         WHERE status = 'ativo' AND data_devolucao_prevista < date('now')""")
        overdue_count = cursor.fetchone()[0]
        
        # Top 5 categorias mais emprestadas
        cursor.execute("""SELECT l.categoria, COUNT(*) as count
                         FROM emprestimos e
                         JOIN livros l ON e.id_livro = l.id
                         WHERE e.data_emprestimo >= date('now', '-12 months')
                         GROUP BY l.categoria
                         ORDER BY count DESC
                         LIMIT 5""")
        top_categories = cursor.fetchall()
    
    return jsonify({
        'monthly_stats': [{'mes': row[0], 'emprestimos': row[1]} for row in monthly_stats],
        'overdue_count': overdue_count,
        'top_categories': [{'categoria': row[0], 'count': row[1]} for row in top_categories]
    })

