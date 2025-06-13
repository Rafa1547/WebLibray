from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'admin':
            flash('Acesso negado. Apenas administradores podem aceder a esta página.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin/utilizadores')
@admin_required
def gerir_utilizadores():
    search = request.args.get('search', '')
    tipo = request.args.get('tipo', '')
    
    conn = sqlite3.connect('db/biblioteca.db')
    c = conn.cursor()
    
    # Base query
    query = "SELECT * FROM utilizadores WHERE 1=1"
    params = []
    
    # Add search filters
    if search:
        query += " AND (nome LIKE ? OR email LIKE ?)"
        params.extend([f'%{search}%', f'%{search}%'])
    
    if tipo and tipo != 'todos':
        query += " AND tipo = ?"
        params.append(tipo)
    
    query += " ORDER BY nome"
    
    c.execute(query, params)
    utilizadores = c.fetchall()
    conn.close()
    
    return render_template('utilizadores/gerir_utilizadores.html', 
                         utilizadores=utilizadores,
                         search=search,
                         tipo_selecionado=tipo)

@admin_bp.route('/admin/utilizadores/add', methods=['GET', 'POST'])
@admin_required
def add_utilizador():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        tipo = request.form['tipo']
        
        # Validation
        if password != confirm_password:
            flash('As passwords não coincidem!', 'error')
            return render_template('utilizadores/add_utilizador.html')
        
        if len(password) < 6:
            flash('A password deve ter pelo menos 6 caracteres!', 'error')
            return render_template('utilizadores/add_utilizador.html')
        
        conn = sqlite3.connect('db/biblioteca.db')
        c = conn.cursor()
        
        # Check if email already exists
        c.execute("SELECT * FROM utilizadores WHERE email = ?", (email,))
        if c.fetchone():
            flash('Este email já está registado!', 'error')
            conn.close()
            return render_template('utilizadores/add_utilizador.html')
        
        # Create new user
        try:
            hashed_password = generate_password_hash(password)
            c.execute("INSERT INTO utilizadores (nome, email, password, tipo) VALUES (?, ?, ?, ?)",
                      (nome, email, hashed_password, tipo))
            conn.commit()
            flash('Utilizador criado com sucesso!', 'success')
            return redirect(url_for('admin.gerir_utilizadores'))
        except Exception as e:
            flash('Erro ao criar utilizador!', 'error')
        finally:
            conn.close()
    
    return render_template('utilizadores/add_utilizador.html')

@admin_bp.route('/admin/utilizadores/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_utilizador(id):
    conn = sqlite3.connect('db/biblioteca.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        tipo = request.form['tipo']
        
        # Check if email exists for other users
        c.execute("SELECT * FROM utilizadores WHERE email = ? AND id != ?", (email, id))
        if c.fetchone():
            flash('Este email já está em uso por outro utilizador!', 'error')
            c.execute("SELECT * FROM utilizadores WHERE id = ?", (id,))
            utilizador = c.fetchone()
            conn.close()
            return render_template('utilizadores/edit_utilizador.html', utilizador=utilizador)
        
        try:
            c.execute("UPDATE utilizadores SET nome = ?, email = ?, tipo = ? WHERE id = ?",
                      (nome, email, tipo, id))
            conn.commit()
            flash('Utilizador atualizado com sucesso!', 'success')
            return redirect(url_for('admin.gerir_utilizadores'))
        except Exception as e:
            flash('Erro ao atualizar utilizador!', 'error')
        finally:
            conn.close()
    
    # GET request
    c.execute("SELECT * FROM utilizadores WHERE id = ?", (id,))
    utilizador = c.fetchone()
    conn.close()
    
    if not utilizador:
        flash('Utilizador não encontrado!', 'error')
        return redirect(url_for('admin.gerir_utilizadores'))
    
    return render_template('utilizadores/edit_utilizador.html', utilizador=utilizador)

@admin_bp.route('/admin/utilizadores/<int:id>/reset-password', methods=['POST'])
@admin_required
def reset_password(id):
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not new_password or len(new_password) < 6:
        flash('A password deve ter pelo menos 6 caracteres!', 'error')
        return redirect(url_for('admin.edit_utilizador', id=id))
    
    if new_password != confirm_password:
        flash('As passwords não coincidem!', 'error')
        return redirect(url_for('admin.edit_utilizador', id=id))
    
    conn = sqlite3.connect('db/biblioteca.db')
    c = conn.cursor()
    
    try:
        hashed_password = generate_password_hash(new_password)
        c.execute("UPDATE utilizadores SET password = ? WHERE id = ?", (hashed_password, id))
        conn.commit()
        flash('Password alterada com sucesso!', 'success')
    except Exception as e:
        flash('Erro ao alterar password!', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('admin.edit_utilizador', id=id))

@admin_bp.route('/admin/utilizadores/<int:id>/delete', methods=['POST'])
@admin_required
def delete_utilizador(id):
    # Prevent deleting yourself
    if id == session.get('user_id'):
        flash('Não pode eliminar a sua própria conta!', 'error')
        return redirect(url_for('admin.gerir_utilizadores'))
    
    conn = sqlite3.connect('db/biblioteca.db')
    c = conn.cursor()
    
    # Check if user has active loans
    c.execute("SELECT COUNT(*) FROM emprestimos WHERE id_utilizador = ? AND status = 'ativo'", (id,))
    active_loans = c.fetchone()[0]
    
    if active_loans > 0:
        flash('Não é possível eliminar este utilizador pois tem empréstimos ativos!', 'error')
        conn.close()
        return redirect(url_for('admin.gerir_utilizadores'))
    
    try:
        # Delete user (loans history will remain for records)
        c.execute("DELETE FROM utilizadores WHERE id = ?", (id,))
        conn.commit()
        flash('Utilizador eliminado com sucesso!', 'success')
    except Exception as e:
        flash('Erro ao eliminar utilizador!', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('admin.gerir_utilizadores'))

@admin_bp.route('/admin/utilizadores/<int:id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(id):
    # This would be for a future feature to temporarily disable users
    # For now, we'll just return a message
    flash('Funcionalidade em desenvolvimento!', 'info')
    return redirect(url_for('admin.gerir_utilizadores'))

@admin_bp.route('/api/admin/stats')
@admin_required
def admin_stats():
    conn = sqlite3.connect('db/biblioteca.db')
    c = conn.cursor()
    
    # User statistics
    c.execute("SELECT tipo, COUNT(*) FROM utilizadores GROUP BY tipo")
    user_stats = dict(c.fetchall())
    
    # Book statistics
    c.execute("SELECT categoria, COUNT(*) FROM livros GROUP BY categoria ORDER BY COUNT(*) DESC LIMIT 5")
    book_categories = c.fetchall()
    
    c.execute("SELECT status, COUNT(*) FROM livros GROUP BY status")
    book_status = dict(c.fetchall())
    
    # Recent activity
    c.execute("""SELECT 'loan' as type, u.nome, l.titulo, e.data_emprestimo as data
                 FROM emprestimos e
                 JOIN utilizadores u ON e.id_utilizador = u.id
                 JOIN livros l ON e.id_livro = l.id
                 WHERE e.data_emprestimo >= date('now', '-7 days')
                 UNION ALL
                 SELECT 'return' as type, u.nome, l.titulo, e.data_devolucao_real as data
                 FROM emprestimos e
                 JOIN utilizadores u ON e.id_utilizador = u.id
                 JOIN livros l ON e.id_livro = l.id
                 WHERE e.data_devolucao_real >= date('now', '-7 days')
                 ORDER BY data DESC
                 LIMIT 10""")
    recent_activity = c.fetchall()
    
    conn.close()
    
    return jsonify({
        'user_stats': user_stats,
        'book_categories': book_categories,
        'book_status': book_status,
        'recent_activity': recent_activity
    })

@admin_bp.route('/admin/relatorios')
@admin_required
def relatorios():
    conn = sqlite3.connect('db/biblioteca.db')
    c = conn.cursor()
    
    # Monthly loan report
    c.execute("""SELECT strftime('%Y-%m', data_emprestimo) as month, 
                        COUNT(*) as total_loans,
                        COUNT(CASE WHEN status = 'devolvido' THEN 1 END) as returned,
                        COUNT(CASE WHEN status = 'atrasado' THEN 1 END) as overdue
                 FROM emprestimos 
                 WHERE data_emprestimo >= date('now', '-12 months')
                 GROUP BY month 
                 ORDER BY month DESC""")
    monthly_report = c.fetchall()
    
    # Top borrowed books
    c.execute("""SELECT l.titulo, l.autor, COUNT(*) as vezes_emprestado
                 FROM emprestimos e
                 JOIN livros l ON e.id_livro = l.id
                 GROUP BY l.id
                 ORDER BY vezes_emprestado DESC
                 LIMIT 10""")
    top_books = c.fetchall()
    
    # Active users
    c.execute("""SELECT u.nome, u.tipo, COUNT(*) as total_emprestimos
                 FROM emprestimos e
                 JOIN utilizadores u ON e.id_utilizador = u.id
                 WHERE e.data_emprestimo >= date('now', '-3 months')
                 GROUP BY u.id
                 ORDER BY total_emprestimos DESC
                 LIMIT 10""")
    active_users = c.fetchall()
    
    conn.close()
    
    return render_template('admin/relatorios.html', 
                         monthly_report=monthly_report,
                         top_books=top_books,
                         active_users=active_users) 