from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.database import get_db_connection
import re
from datetime import datetime

users_bp = Blueprint('users', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@users_bp.route('/perfil')
@login_required
def profile():
    """Visualizar perfil do utilizador"""
    user_id = session.get('user_id')
    
    with get_db_connection() as (conn, cursor):
        # Informações do utilizador
        cursor.execute("SELECT * FROM utilizadores WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        # Estatísticas de empréstimos
        cursor.execute("SELECT COUNT(*) FROM emprestimos WHERE id_utilizador = ?", (user_id,))
        total_emprestimos = cursor.fetchone()[0]
        
        cursor.execute("""SELECT COUNT(*) FROM emprestimos 
                         WHERE id_utilizador = ? AND status = 'ativo'""", (user_id,))
        emprestimos_ativos_count = cursor.fetchone()[0]
        
        # Lista de empréstimos ativos para exibição
        cursor.execute("""SELECT e.*, l.titulo, l.autor, l.capa_url
                         FROM emprestimos e 
                         JOIN livros l ON e.id_livro = l.id 
                         WHERE e.id_utilizador = ? AND e.status = 'ativo'
                         ORDER BY e.data_emprestimo DESC""", (user_id,))
        emprestimos_ativos_raw = cursor.fetchall()
        
        # Calcular dias restantes para cada empréstimo
        emprestimos_ativos = []
        for emp in emprestimos_ativos_raw:
            emprestimo_dict = dict(emp)
            if emp['data_devolucao_prevista']:
                try:
                    data_devolucao = datetime.fromisoformat(emp['data_devolucao_prevista'])
                    hoje = datetime.now()
                    dias_restantes = (data_devolucao.date() - hoje.date()).days
                    emprestimo_dict['dias_restantes'] = dias_restantes
                except:
                    emprestimo_dict['dias_restantes'] = 0
            else:
                emprestimo_dict['dias_restantes'] = 0
            emprestimos_ativos.append(emprestimo_dict)
        
        cursor.execute("""SELECT COUNT(*) FROM emprestimos 
                         WHERE id_utilizador = ? AND status = 'devolvido'""", (user_id,))
        emprestimos_devolvidos = cursor.fetchone()[0]
        
        cursor.execute("""SELECT COUNT(*) FROM emprestimos 
                         WHERE id_utilizador = ? AND status = 'atrasado'""", (user_id,))
        emprestimos_atrasados = cursor.fetchone()[0]
        
        # Empréstimos recentes
        cursor.execute("""SELECT e.*, l.titulo, l.autor, l.capa_url
                         FROM emprestimos e 
                         JOIN livros l ON e.id_livro = l.id 
                         WHERE e.id_utilizador = ?
                         ORDER BY e.data_emprestimo DESC LIMIT 5""", (user_id,))
        emprestimos_recentes = cursor.fetchall()
        
        # Categorias favoritas
        cursor.execute("""SELECT l.categoria, COUNT(*) as count
                         FROM emprestimos e
                         JOIN livros l ON e.id_livro = l.id
                         WHERE e.id_utilizador = ?
                         GROUP BY l.categoria
                         ORDER BY count DESC
                         LIMIT 3""", (user_id,))
        categorias_favoritas_raw = cursor.fetchall()
        
        # Converter para lista de dicionários para melhor acesso no template
        categorias_favoritas = []
        for cat in categorias_favoritas_raw:
            categorias_favoritas.append({
                'categoria': cat[0],
                'count': cat[1]
            })
        
        # Contar livros únicos emprestados (para favoritos)
        cursor.execute("""SELECT COUNT(DISTINCT e.id_livro) 
                         FROM emprestimos e 
                         WHERE e.id_utilizador = ?""", (user_id,))
        livros_favoritos = cursor.fetchone()[0]
    
    # Estruturar estatísticas para o template
    stats = {
        'emprestimos_ativos': emprestimos_ativos_count,
        'total_emprestimos': total_emprestimos,
        'livros_favoritos': livros_favoritos
    }
    
    return render_template('users/profile.html',
                         utilizador=user,
                         stats=stats,
                         total_emprestimos=total_emprestimos,
                         emprestimos_ativos=emprestimos_ativos,
                         emprestimos_devolvidos=emprestimos_devolvidos,
                         emprestimos_atrasados=emprestimos_atrasados,
                         emprestimos_recentes=emprestimos_recentes,
                         categorias_favoritas=categorias_favoritas)

@users_bp.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Editar perfil do utilizador"""
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        # Obter dados do formulário
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        telefone = request.form.get('telefone', '').strip()
        data_nascimento = request.form.get('data_nascimento', '').strip()
        endereco = request.form.get('endereco', '').strip()
        biografia = request.form.get('biografia', '').strip()
        notificacoes_email = 1 if 'notificacoes_email' in request.form else 0
        lembretes_devolucao = 1 if 'lembretes_devolucao' in request.form else 0
        
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
        
        # Validar telefone (opcional)
        if telefone:
            # Limpar telefone (remover espaços, hífens, parênteses)
            telefone_clean = re.sub(r'[^\d+]', '', telefone)
            if len(telefone_clean) < 9 or len(telefone_clean) > 15:
                errors.append('Telefone deve ter entre 9 e 15 dígitos.')
            telefone = telefone_clean
        
        # Validar data de nascimento (opcional)
        if data_nascimento:
            try:
                birth_date = datetime.strptime(data_nascimento, '%Y-%m-%d')
                today = datetime.now()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                if age < 10 or age > 120:
                    errors.append('Data de nascimento deve representar idade entre 10 e 120 anos.')
            except ValueError:
                errors.append('Formato de data de nascimento inválido.')
        
        # Validar endereço (opcional)
        if endereco and len(endereco) > 200:
            errors.append('Endereço muito longo (máximo 200 caracteres).')
        
        # Validar biografia (opcional)
        if biografia and len(biografia) > 500:
            errors.append('Biografia muito longa (máximo 500 caracteres).')
        
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
            # Atualizar perfil
            try:
                with get_db_connection() as (conn, cursor):
                    cursor.execute("""UPDATE utilizadores SET 
                                     nome = ?, email = ?, telefone = ?, data_nascimento = ?,
                                     endereco = ?, biografia = ?, notificacoes_email = ?,
                                     lembretes_devolucao = ?
                                     WHERE id = ?""",
                                  (nome, email, telefone or None, data_nascimento or None,
                                   endereco or None, biografia or None, notificacoes_email,
                                   lembretes_devolucao, user_id))
                    conn.commit()
                
                # Atualizar nome na sessão
                session['user_name'] = nome
                
                flash('Perfil atualizado com sucesso!', 'success')
                return redirect(url_for('users.profile'))
                
            except Exception as e:
                flash('Erro ao atualizar perfil. Tente novamente.', 'error')
    
    # GET request - mostrar formulário
    with get_db_connection() as (conn, cursor):
        cursor.execute("SELECT * FROM utilizadores WHERE id = ?", (user_id,))
        user = cursor.fetchone()
    
    return render_template('users/edit_profile.html', user=user)

@users_bp.route('/perfil/alterar-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Alterar password do utilizador"""
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validações
        errors = []
        
        if not current_password:
            errors.append('Password atual é obrigatória.')
        
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
        
        # Verificar password atual
        if not errors:
            with get_db_connection() as (conn, cursor):
                cursor.execute("SELECT password FROM utilizadores WHERE id = ?", (user_id,))
                user = cursor.fetchone()
                
                if not user or not check_password_hash(user['password'], current_password):
                    errors.append('Password atual incorreta.')
        
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
                
                flash('Password alterada com sucesso!', 'success')
                return redirect(url_for('users.profile'))
                
            except Exception as e:
                flash('Erro ao alterar password. Tente novamente.', 'error')
    
    return render_template('users/change_password.html')

@users_bp.route('/perfil/historico')
@login_required
def loan_history():
    """Histórico completo de empréstimos do utilizador"""
    user_id = session.get('user_id')
    
    # Filtros
    status_filter = request.args.get('status', '')
    
    with get_db_connection() as (conn, cursor):
        query = """SELECT e.*, l.titulo, l.autor, l.capa_url
                   FROM emprestimos e 
                   JOIN livros l ON e.id_livro = l.id 
                   WHERE e.id_utilizador = ?"""
        params = [user_id]
        
        if status_filter:
            query += " AND e.status = ?"
            params.append(status_filter)
        
        query += " ORDER BY e.data_emprestimo DESC"
        cursor.execute(query, params)
        emprestimos = cursor.fetchall()
    
    return render_template('users/loan_history.html', 
                         emprestimos=emprestimos, 
                         status_filter=status_filter)

