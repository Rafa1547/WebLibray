from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from src.models.database import get_db_connection
import os
import re
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'admin':
            flash('Acesso negado. Apenas administradores podem aceder a esta página.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# ===== GESTÃO DE UTILIZADORES =====

@admin_bp.route('/admin/utilizadores')
@admin_required
def manage_users():
    """Listar e gerir utilizadores"""
    search = request.args.get('search', '').strip()
    tipo_filter = request.args.get('tipo', '')
    
    with get_db_connection() as (conn, cursor):
        query = "SELECT * FROM utilizadores WHERE 1=1"
        params = []
        
        if search:
            query += " AND (nome LIKE ? OR email LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
        
        if tipo_filter:
            query += " AND tipo = ?"
            params.append(tipo_filter)
        
        query += " ORDER BY nome"
        cursor.execute(query, params)
        utilizadores = cursor.fetchall()
    
    return render_template('admin/manage_users.html', 
                         utilizadores=utilizadores, 
                         search=search, 
                         tipo_filter=tipo_filter)

@admin_bp.route('/admin/utilizadores/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    """Adicionar novo utilizador"""
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        tipo = request.form.get('tipo', '')
        
        # Validações
        errors = []
        
        # Validar nome
        if not nome:
            errors.append('Nome é obrigatório.')
        elif len(nome) < 2:
            errors.append('Nome deve ter pelo menos 2 caracteres.')
        elif len(nome) > 100:
            errors.append('Nome muito longo (máximo 100 caracteres).')
        elif not nome.replace(' ', '').replace('-', '').replace("'", '').isalpha():
            errors.append('Nome deve conter apenas letras, espaços, hífens e apóstrofes.')
        
        # Validar email
        email_regex = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
        if not email:
            errors.append('Email é obrigatório.')
        elif not re.match(email_regex, email):
            errors.append('Formato de email inválido.')
        
        # Validar password
        if not password:
            errors.append('Password é obrigatória.')
        elif len(password) < 6:
            errors.append('Password deve ter pelo menos 6 caracteres.')
        elif len(password) > 128:
            errors.append('Password muito longa (máximo 128 caracteres).')
        
        # Validar confirmação de password
        if not confirm_password:
            errors.append('Confirmação de password é obrigatória.')
        elif password != confirm_password:
            errors.append('As passwords não coincidem.')
        
        # Validar tipo
        valid_types = ['admin', 'aluno', 'professor']
        if not tipo:
            errors.append('Tipo de utilizador é obrigatório.')
        elif tipo not in valid_types:
            errors.append('Tipo de utilizador inválido.')
        
        # Verificar se email já existe
        if not errors:
            with get_db_connection() as (conn, cursor):
                cursor.execute("SELECT id FROM utilizadores WHERE email = ?", (email,))
                if cursor.fetchone():
                    errors.append('Este email já está registado.')
        
        # Se há erros, mostrar e voltar ao formulário
        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            # Criar utilizador
            try:
                with get_db_connection() as (conn, cursor):
                    hashed_password = generate_password_hash(password)
                    cursor.execute("""INSERT INTO utilizadores (nome, email, password, tipo) 
                                     VALUES (?, ?, ?, ?)""",
                                  (nome, email, hashed_password, tipo))
                    conn.commit()
                
                flash(f'Utilizador "{nome}" criado com sucesso!', 'success')
                return redirect(url_for('admin.manage_users'))
                
            except Exception as e:
                flash('Erro ao criar utilizador. Tente novamente.', 'error')
    
    return render_template('admin/add_user.html')

@admin_bp.route('/admin/utilizadores/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Editar utilizador"""
    with get_db_connection() as (conn, cursor):
        cursor.execute("SELECT * FROM utilizadores WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            flash('Utilizador não encontrado.', 'error')
            return redirect(url_for('admin.manage_users'))
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        tipo = request.form.get('tipo', '')
        
        # Validações
        errors = []
        
        # Validar nome
        if not nome:
            errors.append('Nome é obrigatório.')
        elif len(nome) < 2:
            errors.append('Nome deve ter pelo menos 2 caracteres.')
        elif len(nome) > 100:
            errors.append('Nome muito longo (máximo 100 caracteres).')
        elif not nome.replace(' ', '').replace('-', '').replace("'", '').isalpha():
            errors.append('Nome deve conter apenas letras, espaços, hífens e apóstrofes.')
        
        # Validar email
        email_regex = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
        if not email:
            errors.append('Email é obrigatório.')
        elif not re.match(email_regex, email):
            errors.append('Formato de email inválido.')
        
        # Validar tipo
        valid_types = ['admin', 'aluno', 'professor']
        if not tipo:
            errors.append('Tipo de utilizador é obrigatório.')
        elif tipo not in valid_types:
            errors.append('Tipo de utilizador inválido.')
        
        # Verificar se email já existe (exceto o próprio utilizador)
        if not errors:
            with get_db_connection() as (conn, cursor):
                cursor.execute("SELECT id FROM utilizadores WHERE email = ? AND id != ?", (email, user_id))
                if cursor.fetchone():
                    errors.append('Este email já está registado por outro utilizador.')
        
        # Se há erros, mostrar e voltar ao formulário
        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            # Atualizar utilizador
            try:
                with get_db_connection() as (conn, cursor):
                    cursor.execute("""UPDATE utilizadores SET nome = ?, email = ?, tipo = ? 
                                     WHERE id = ?""",
                                  (nome, email, tipo, user_id))
                    conn.commit()
                
                flash(f'Utilizador "{nome}" atualizado com sucesso!', 'success')
                return redirect(url_for('admin.manage_users'))
                
            except Exception as e:
                flash('Erro ao atualizar utilizador. Tente novamente.', 'error')
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/admin/utilizadores/<int:user_id>/reset-password', methods=['GET', 'POST'])
@admin_required
def reset_user_password(user_id):
    """Reset password de utilizador"""
    with get_db_connection() as (conn, cursor):
        cursor.execute("SELECT * FROM utilizadores WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            flash('Utilizador não encontrado.', 'error')
            return redirect(url_for('admin.manage_users'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validações
        errors = []
        
        if not new_password:
            errors.append('Nova password é obrigatória.')
        elif len(new_password) < 6:
            errors.append('Nova password deve ter pelo menos 6 caracteres.')
        elif len(new_password) > 128:
            errors.append('Nova password muito longa (máximo 128 caracteres).')
        
        if not confirm_password:
            errors.append('Confirmação de password é obrigatória.')
        elif new_password != confirm_password:
            errors.append('As passwords não coincidem.')
        
        # Se há erros, mostrar e voltar ao formulário
        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            # Atualizar password
            try:
                with get_db_connection() as (conn, cursor):
                    hashed_password = generate_password_hash(new_password)
                    cursor.execute("UPDATE utilizadores SET password = ? WHERE id = ?",
                                  (hashed_password, user_id))
                    conn.commit()
                
                flash(f'Password do utilizador "{user["nome"]}" alterada com sucesso!', 'success')
                return redirect(url_for('admin.manage_users'))
                
            except Exception as e:
                flash('Erro ao alterar password. Tente novamente.', 'error')
    
    return render_template('admin/reset_password.html', user=user)

@admin_bp.route('/admin/utilizadores/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Eliminar utilizador"""
    current_user_id = session.get('user_id')
    
    # Não permitir auto-eliminação
    if user_id == current_user_id:
        flash('Não pode eliminar a sua própria conta.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    with get_db_connection() as (conn, cursor):
        # Verificar se utilizador existe
        cursor.execute("SELECT * FROM utilizadores WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            flash('Utilizador não encontrado.', 'error')
            return redirect(url_for('admin.manage_users'))
        
        # Verificar se tem empréstimos ativos
        cursor.execute("SELECT COUNT(*) FROM emprestimos WHERE id_utilizador = ? AND status = 'ativo'", 
                      (user_id,))
        active_loans = cursor.fetchone()[0]
        
        if active_loans > 0:
            flash(f'Não é possível eliminar o utilizador "{user["nome"]}" porque tem {active_loans} empréstimo(s) ativo(s).', 'error')
            return redirect(url_for('admin.manage_users'))
        
        # Eliminar utilizador
        try:
            cursor.execute("DELETE FROM utilizadores WHERE id = ?", (user_id,))
            conn.commit()
            
            flash(f'Utilizador "{user["nome"]}" eliminado com sucesso!', 'success')
            
        except Exception as e:
            flash('Erro ao eliminar utilizador. Tente novamente.', 'error')
    
    return redirect(url_for('admin.manage_users'))

# ===== GESTÃO DE LIVROS =====

@admin_bp.route('/admin/livros')
@admin_required
def manage_books():
    """Listar e gerir livros"""
    search = request.args.get('search', '').strip()
    categoria_filter = request.args.get('categoria', '')
    status_filter = request.args.get('status', '')
    
    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    
    with get_db_connection() as (conn, cursor):
        # Contar total de registros
        count_query = "SELECT COUNT(*) FROM livros WHERE 1=1"
        count_params = []
        
        if search:
            count_query += " AND (titulo LIKE ? OR autor LIKE ? OR isbn LIKE ?)"
            search_param = f"%{search}%"
            count_params.extend([search_param, search_param, search_param])
        
        if categoria_filter:
            count_query += " AND categoria = ?"
            count_params.append(categoria_filter)
        
        if status_filter:
            count_query += " AND status = ?"
            count_params.append(status_filter)
        
        cursor.execute(count_query, count_params)
        total_records = cursor.fetchone()[0]
        
        # Calcular paginação
        total_pages = max(1, (total_records + per_page - 1) // per_page)
        page = max(1, min(page, total_pages))
        offset = (page - 1) * per_page
        
        # Buscar livros com paginação
        query = "SELECT * FROM livros WHERE 1=1"
        params = []
        
        if search:
            query += " AND (titulo LIKE ? OR autor LIKE ? OR isbn LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        if categoria_filter:
            query += " AND categoria = ?"
            params.append(categoria_filter)
        
        if status_filter:
            query += " AND status = ?"
            params.append(status_filter)
        
        query += " ORDER BY titulo LIMIT ? OFFSET ?"
        params.extend([per_page, offset])
        cursor.execute(query, params)
        livros = cursor.fetchall()
        
        # Obter categorias para filtro
        cursor.execute("SELECT DISTINCT categoria FROM livros ORDER BY categoria")
        categorias = [row[0] for row in cursor.fetchall()]
    
    # Preparar variáveis de paginação
    has_prev = page > 1
    has_next = page < total_pages
    prev_page = page - 1 if has_prev else None
    next_page = page + 1 if has_next else None
    
    # Gerar números de página para exibir
    page_numbers = []
    if total_pages <= 7:
        page_numbers = list(range(1, total_pages + 1))
    else:
        if page <= 4:
            page_numbers = list(range(1, 6)) + ['...', total_pages]
        elif page >= total_pages - 3:
            page_numbers = [1, '...'] + list(range(total_pages - 4, total_pages + 1))
        else:
            page_numbers = [1, '...'] + list(range(page - 1, page + 2)) + ['...', total_pages]
    
    def build_url(**kwargs):
        """Função auxiliar para construir URLs de paginação"""
        args = {
            'search': search,
            'categoria': categoria_filter,
            'status': status_filter,
            'per_page': per_page
        }
        args.update(kwargs)
        # Remove parâmetros vazios
        args = {k: v for k, v in args.items() if v}
        query_string = '&'.join(f"{k}={v}" for k, v in args.items())
        return f"{url_for('admin.manage_books')}?{query_string}"
    
    return render_template('books/catalog.html', 
                         livros=livros, 
                         categorias=categorias,
                         search=search, 
                         categoria_filter=categoria_filter,
                         status_filter=status_filter,
                         categoria=categoria_filter,  # Alias para o template
                         total_records=total_records,
                         total_pages=total_pages,
                         page=page,
                         per_page=per_page,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_page=prev_page,
                         next_page=next_page,
                         page_numbers=page_numbers,
                         build_url=build_url,
                         sort_by='titulo',  # Padrão para o template
                         order='asc',       # Padrão para o template
                         is_admin=True)

# ===== RELATÓRIOS =====

@admin_bp.route('/admin/relatorios')
@admin_required
def reports():
    """Página de relatórios administrativos"""
    # Obter filtros de período
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    periodo = request.args.get('periodo')
    
    # Definir período baseado na seleção
    if periodo == '7dias':
        data_inicio = None
        data_fim = None
        periodo_sql = "date('now', '-7 days')"
    elif periodo == '30dias':
        data_inicio = None
        data_fim = None
        periodo_sql = "date('now', '-30 days')"
    elif periodo == '3meses':
        data_inicio = None
        data_fim = None
        periodo_sql = "date('now', '-3 months')"
    elif periodo == 'ano':
        data_inicio = None
        data_fim = None
        periodo_sql = "date('now', 'start of year')"
    else:
        periodo_sql = None
    
    with get_db_connection() as (conn, cursor):
        # Estatísticas gerais
        cursor.execute("SELECT COUNT(*) FROM livros")
        total_livros = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM livros WHERE status = 'disponivel'")
        livros_disponiveis = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM livros WHERE status = 'emprestado'")
        livros_emprestados = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM utilizadores WHERE tipo != 'admin'")
        total_utilizadores = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM emprestimos")
        total_emprestimos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM emprestimos WHERE status = 'ativo'")
        emprestimos_ativos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM emprestimos WHERE status = 'atrasado'")
        emprestimos_atrasados = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM emprestimos WHERE status = 'devolvido'")
        emprestimos_devolvidos = cursor.fetchone()[0]
        
        # Taxa de utilização
        taxa_utilizacao = round((livros_emprestados / total_livros * 100) if total_livros > 0 else 0, 1)
        
        # Estatísticas do período filtrado
        periodo_filtro = ""
        if periodo_sql:
            periodo_filtro = f" AND data_emprestimo >= {periodo_sql}"
        elif data_inicio and data_fim:
            periodo_filtro = f" AND date(data_emprestimo) BETWEEN '{data_inicio}' AND '{data_fim}'"
        elif data_inicio:
            periodo_filtro = f" AND date(data_emprestimo) >= '{data_inicio}'"
        elif data_fim:
            periodo_filtro = f" AND date(data_emprestimo) <= '{data_fim}'"
        
        # Empréstimos no período
        cursor.execute(f"SELECT COUNT(*) FROM emprestimos WHERE 1=1{periodo_filtro}")
        emprestimos_periodo = cursor.fetchone()[0]
        
        # Top 10 livros mais emprestados
        cursor.execute(f"""SELECT l.titulo, l.autor, COUNT(*) as total_emprestimos
                         FROM emprestimos e
                         JOIN livros l ON e.id_livro = l.id
                         WHERE 1=1{periodo_filtro}
                         GROUP BY l.id, l.titulo, l.autor
                         ORDER BY total_emprestimos DESC
                         LIMIT 10""")
        top_livros = cursor.fetchall()
        
        # Utilizadores mais ativos
        cursor.execute(f"""SELECT u.nome, u.email, u.tipo, COUNT(*) as total_emprestimos
                         FROM emprestimos e
                         JOIN utilizadores u ON e.id_utilizador = u.id
                         WHERE 1=1{periodo_filtro}
                         GROUP BY u.id, u.nome, u.email, u.tipo
                         ORDER BY total_emprestimos DESC
                         LIMIT 10""")
        utilizadores_ativos = cursor.fetchall()
        
        # Estatísticas mensais dos últimos 12 meses (para gráfico)
        cursor.execute("""SELECT 
                            strftime('%Y-%m', data_emprestimo) as mes,
                            COUNT(*) as emprestimos,
                            COUNT(CASE WHEN status = 'devolvido' THEN 1 END) as devolucoes,
                            COUNT(CASE WHEN status = 'atrasado' THEN 1 END) as atrasos
                         FROM emprestimos 
                         WHERE data_emprestimo >= date('now', '-12 months')
                         GROUP BY strftime('%Y-%m', data_emprestimo)
                         ORDER BY mes""")
        monthly_report = cursor.fetchall()
        
        # Preparar dados para gráfico mensal
        months_pt = {
            '01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr', 
            '05': 'Mai', '06': 'Jun', '07': 'Jul', '08': 'Ago',
            '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'
        }
        
        chart_data = {
            'labels': [months_pt.get(row[0].split('-')[1], row[0]) for row in monthly_report],
            'emprestimos': [row[1] for row in monthly_report],
            'devolucoes': [row[2] for row in monthly_report],
            'atrasos': [row[3] for row in monthly_report]
        }
        
        # Categorias mais populares (sempre últimos 12 meses para o gráfico)
        cursor.execute("""SELECT l.categoria, COUNT(*) as count
                         FROM emprestimos e
                         JOIN livros l ON e.id_livro = l.id
                         WHERE e.data_emprestimo >= date('now', '-12 months')
                         GROUP BY l.categoria
                         ORDER BY count DESC
                         LIMIT 8""")
        categories_data = cursor.fetchall()
        
        categorias_chart = {
            'labels': [row[0] for row in categories_data] if categories_data else [],
            'data': [row[1] for row in categories_data] if categories_data else []
        }
        
        # Empréstimos em atraso detalhados
        cursor.execute("""SELECT 
                            l.titulo, l.autor, u.nome, u.email,
                            e.data_emprestimo, e.data_devolucao_prevista,
                            CAST(julianday('now') - julianday(e.data_devolucao_prevista) AS INTEGER) as dias_atraso
                         FROM emprestimos e
                         JOIN livros l ON e.id_livro = l.id
                         JOIN utilizadores u ON e.id_utilizador = u.id
                         WHERE e.status = 'atrasado'
                         ORDER BY dias_atraso DESC""")
        atrasos_detalhados = cursor.fetchall()
        
        # Novas estatísticas adicionais
        cursor.execute("SELECT COUNT(DISTINCT categoria) FROM livros")
        total_categorias = cursor.fetchone()[0]
        
        cursor.execute("""SELECT AVG(emprestimos_por_usuario) 
                         FROM (SELECT COUNT(*) as emprestimos_por_usuario 
                               FROM emprestimos 
                               GROUP BY id_utilizador)""")
        media_emprestimos = cursor.fetchone()[0] or 0
        media_emprestimos = round(media_emprestimos, 1)
        
        # Categoria mais popular
        cursor.execute("""SELECT l.categoria, COUNT(*) as count
                         FROM emprestimos e
                         JOIN livros l ON e.id_livro = l.id
                         GROUP BY l.categoria
                         ORDER BY count DESC
                         LIMIT 1""")
        categoria_popular = cursor.fetchone()
        categoria_popular = categoria_popular[0] if categoria_popular else "N/A"
    
    return render_template('admin/reports.html',
                         total_livros=total_livros,
                         livros_disponiveis=livros_disponiveis,
                         livros_emprestados=livros_emprestados,
                         total_utilizadores=total_utilizadores,
                         total_emprestimos=total_emprestimos,
                         emprestimos_ativos=emprestimos_ativos,
                         emprestimos_atrasados=emprestimos_atrasados,
                         emprestimos_devolvidos=emprestimos_devolvidos,
                         emprestimos_periodo=emprestimos_periodo,
                         taxa_utilizacao=taxa_utilizacao,
                         total_categorias=total_categorias,
                         media_emprestimos=media_emprestimos,
                         categoria_popular=categoria_popular,
                         top_livros=top_livros,
                         utilizadores_ativos=utilizadores_ativos,
                         atrasos_detalhados=atrasos_detalhados,
                         monthly_report=monthly_report,
                         chart_data=chart_data,
                         categorias_chart=categorias_chart,
                         periodo_selecionado=periodo,
                         data_inicio=data_inicio,
                         data_fim=data_fim)

@admin_bp.route('/api/admin/stats')
@admin_required
def admin_stats():
    """API para estatísticas administrativas"""
    with get_db_connection() as (conn, cursor):
        # Contadores gerais
        cursor.execute("SELECT COUNT(*) FROM livros")
        total_livros = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM utilizadores")
        total_utilizadores = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM emprestimos WHERE status = 'ativo'")
        emprestimos_ativos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM emprestimos WHERE status = 'atrasado'")
        emprestimos_atrasados = cursor.fetchone()[0]
        
        # Estatísticas mensais
        cursor.execute("""SELECT 
                            strftime('%Y-%m', data_emprestimo) as mes,
                            COUNT(*) as total
                         FROM emprestimos 
                         WHERE data_emprestimo >= date('now', '-12 months')
                         GROUP BY strftime('%Y-%m', data_emprestimo)
                         ORDER BY mes""")
        monthly_stats = cursor.fetchall()
        
        # Top categorias
        cursor.execute("""SELECT l.categoria, COUNT(*) as count
                         FROM emprestimos e
                         JOIN livros l ON e.id_livro = l.id
                         WHERE e.data_emprestimo >= date('now', '-6 months')
                         GROUP BY l.categoria
                         ORDER BY count DESC
                         LIMIT 5""")
        top_categories = cursor.fetchall()
    
    return jsonify({
        'totals': {
            'livros': total_livros,
            'utilizadores': total_utilizadores,
            'emprestimos_ativos': emprestimos_ativos,
            'emprestimos_atrasados': emprestimos_atrasados
        },
        'monthly_stats': [{'mes': row[0], 'total': row[1]} for row in monthly_stats],
        'top_categories': [{'categoria': row[0], 'count': row[1]} for row in top_categories]
    })

