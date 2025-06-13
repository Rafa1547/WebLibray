from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

profile_bp = Blueprint('profile', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@profile_bp.route('/perfil')
@login_required
def perfil():
    user_id = session.get('user_id')
    
    conn = sqlite3.connect('db/biblioteca.db')
    c = conn.cursor()
    
    # Get user info
    c.execute("SELECT * FROM utilizadores WHERE id = ?", (user_id,))
    user = c.fetchone()
    
    # Get user's loan statistics
    c.execute("SELECT COUNT(*) FROM emprestimos WHERE id_utilizador = ?", (user_id,))
    total_emprestimos = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM emprestimos WHERE id_utilizador = ? AND status = 'ativo'", (user_id,))
    emprestimos_ativos = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM emprestimos WHERE id_utilizador = ? AND status = 'devolvido'", (user_id,))
    emprestimos_devolvidos = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM emprestimos WHERE id_utilizador = ? AND status = 'atrasado'", (user_id,))
    emprestimos_atrasados = c.fetchone()[0]
    
    # Get recent loans
    c.execute("""SELECT e.*, l.titulo, l.autor, l.capa_url 
                 FROM emprestimos e 
                 JOIN livros l ON e.id_livro = l.id 
                 WHERE e.id_utilizador = ? 
                 ORDER BY e.data_emprestimo DESC 
                 LIMIT 5""", (user_id,))
    emprestimos_recentes = c.fetchall()
    
    # Get favorite categories
    c.execute("""SELECT l.categoria, COUNT(*) as count
                 FROM emprestimos e
                 JOIN livros l ON e.id_livro = l.id
                 WHERE e.id_utilizador = ?
                 GROUP BY l.categoria
                 ORDER BY count DESC
                 LIMIT 3""", (user_id,))
    categorias_favoritas = c.fetchall()
    
    conn.close()
    
    return render_template('utilizadores/perfil.html', 
                         user=user,
                         total_emprestimos=total_emprestimos,
                         emprestimos_ativos=emprestimos_ativos,
                         emprestimos_devolvidos=emprestimos_devolvidos,
                         emprestimos_atrasados=emprestimos_atrasados,
                         emprestimos_recentes=emprestimos_recentes,
                         categorias_favoritas=categorias_favoritas)

@profile_bp.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    user_id = session.get('user_id')
    
    conn = sqlite3.connect('db/biblioteca.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        
        # Check if email exists for other users
        c.execute("SELECT * FROM utilizadores WHERE email = ? AND id != ?", (email, user_id))
        if c.fetchone():
            flash('Este email já está em uso!', 'error')
            c.execute("SELECT * FROM utilizadores WHERE id = ?", (user_id,))
            user = c.fetchone()
            conn.close()
            return render_template('utilizadores/editar_perfil.html', user=user)
        
        try:
            c.execute("UPDATE utilizadores SET nome = ?, email = ? WHERE id = ?",
                      (nome, email, user_id))
            conn.commit()
            session['user_name'] = nome  # Update session
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('profile.perfil'))
        except Exception as e:
            flash('Erro ao atualizar perfil!', 'error')
        finally:
            conn.close()
    
    # GET request
    c.execute("SELECT * FROM utilizadores WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    
    return render_template('utilizadores/editar_perfil.html', user=user)

@profile_bp.route('/perfil/alterar-password', methods=['GET', 'POST'])
@login_required
def alterar_password():
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        if len(new_password) < 6:
            flash('A nova password deve ter pelo menos 6 caracteres!', 'error')
            return render_template('utilizadores/alterar_password.html')
        
        if new_password != confirm_password:
            flash('As passwords não coincidem!', 'error')
            return render_template('utilizadores/alterar_password.html')
        
        conn = sqlite3.connect('db/biblioteca.db')
        c = conn.cursor()
        
        # Verify current password
        c.execute("SELECT password FROM utilizadores WHERE id = ?", (user_id,))
        user = c.fetchone()
        
        if not user or not check_password_hash(user[0], current_password):
            flash('Password atual incorreta!', 'error')
            conn.close()
            return render_template('utilizadores/alterar_password.html')
        
        try:
            hashed_password = generate_password_hash(new_password)
            c.execute("UPDATE utilizadores SET password = ? WHERE id = ?", (hashed_password, user_id))
            conn.commit()
            flash('Password alterada com sucesso!', 'success')
            return redirect(url_for('profile.perfil'))
        except Exception as e:
            flash('Erro ao alterar password!', 'error')
        finally:
            conn.close()
    
    return render_template('utilizadores/alterar_password.html')

@profile_bp.route('/perfil/historico')
@login_required
def historico_emprestimos():
    user_id = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    conn = sqlite3.connect('db/biblioteca.db')
    c = conn.cursor()
    
    # Get total count
    c.execute("SELECT COUNT(*) FROM emprestimos WHERE id_utilizador = ?", (user_id,))
    total = c.fetchone()[0]
    
    # Get paginated results
    offset = (page - 1) * per_page
    c.execute("""SELECT e.*, l.titulo, l.autor, l.capa_url 
                 FROM emprestimos e 
                 JOIN livros l ON e.id_livro = l.id 
                 WHERE e.id_utilizador = ? 
                 ORDER BY e.data_emprestimo DESC 
                 LIMIT ? OFFSET ?""", (user_id, per_page, offset))
    emprestimos = c.fetchall()
    
    conn.close()
    
    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    return render_template('utilizadores/historico_emprestimos.html', 
                         emprestimos=emprestimos,
                         page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         total=total)

@profile_bp.route('/perfil/favoritos')
@login_required
def livros_favoritos():
    # This would be for a future feature to mark books as favorites
    # For now, we'll show most borrowed categories
    user_id = session.get('user_id')
    
    conn = sqlite3.connect('db/biblioteca.db')
    c = conn.cursor()
    
    # Get books from user's favorite categories
    c.execute("""SELECT l.categoria, COUNT(*) as count
                 FROM emprestimos e
                 JOIN livros l ON e.id_livro = l.id
                 WHERE e.id_utilizador = ?
                 GROUP BY l.categoria
                 ORDER BY count DESC""", (user_id,))
    categorias = c.fetchall()
    
    # Get recommended books based on user's history
    recommended_books = []
    if categorias:
        top_category = categorias[0][0]
        c.execute("""SELECT DISTINCT l.* FROM livros l
                     LEFT JOIN emprestimos e ON l.id = e.id_livro AND e.id_utilizador = ?
                     WHERE l.categoria = ? AND l.status = 'disponivel' AND e.id IS NULL
                     ORDER BY l.data_adicao DESC
                     LIMIT 6""", (user_id, top_category))
        recommended_books = c.fetchall()
    
    conn.close()
    
    return render_template('utilizadores/livros_favoritos.html', 
                         categorias=categorias,
                         recommended_books=recommended_books) 