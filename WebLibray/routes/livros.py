from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime

livros_bp = Blueprint('livros', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@livros_bp.route('/livros')
def ver_livros():
    search = request.args.get('search', '')
    categoria = request.args.get('categoria', '')
    
    conn = sqlite3.connect('db/biblioteca.db')
    c = conn.cursor()
    
    # Base query
    query = "SELECT * FROM livros WHERE 1=1"
    params = []
    
    # Add search filters
    if search:
        query += " AND (titulo LIKE ? OR autor LIKE ?)"
        params.extend([f'%{search}%', f'%{search}%'])
    
    if categoria and categoria != 'todas':
        query += " AND categoria = ?"
        params.append(categoria)
    
    query += " ORDER BY titulo"
    
    c.execute(query, params)
    livros = c.fetchall()
    
    # Get all categories for filter
    c.execute("SELECT DISTINCT categoria FROM livros ORDER BY categoria")
    categorias = [row[0] for row in c.fetchall()]
    
    conn.close()
    
    return render_template('livros/ver_livros.html', 
                         livros=livros, 
                         categorias=categorias,
                         search=search,
                         categoria_selecionada=categoria)

@livros_bp.route('/livros/<int:id>')
def detalhes_livro(id):
    conn = sqlite3.connect('db/biblioteca.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM livros WHERE id = ?", (id,))
    livro = c.fetchone()
    
    if not livro:
        flash('Livro não encontrado!', 'error')
        return redirect(url_for('livros.ver_livros'))
    
    # Check if user can borrow this book
    pode_emprestar = False
    if 'user_id' in session and session.get('user_type') in ['aluno', 'professor']:
        if livro[6] == 'disponivel':  # status column
            # Check if user doesn't have this book already borrowed
            c.execute("SELECT * FROM emprestimos WHERE id_utilizador = ? AND id_livro = ? AND status = 'ativo'", 
                     (session['user_id'], id))
            if not c.fetchone():
                pode_emprestar = True
    
    conn.close()
    
    return render_template('livros/detalhes_livro.html', 
                         livro=livro, 
                         pode_emprestar=pode_emprestar)

@livros_bp.route('/admin/livros/add', methods=['GET', 'POST'])
def add_livro():
    if session.get('user_type') != 'admin':
        flash('Acesso negado!', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        categoria = request.form['categoria']
        isbn = request.form['isbn']
        descricao = request.form['descricao']
        
        # Handle file upload
        capa_url = None
        if 'capa' in request.files:
            file = request.files['capa']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file_path = os.path.join('static/images/covers', filename)
                file.save(file_path)
                capa_url = f'images/covers/{filename}'
        
        conn = sqlite3.connect('db/biblioteca.db')
        c = conn.cursor()
        
        try:
            c.execute("""INSERT INTO livros (titulo, autor, categoria, isbn, capa_url, descricao) 
                         VALUES (?, ?, ?, ?, ?, ?)""",
                      (titulo, autor, categoria, isbn, capa_url, descricao))
            conn.commit()
            flash('Livro adicionado com sucesso!', 'success')
            return redirect(url_for('livros.ver_livros'))
        except sqlite3.IntegrityError:
            flash('ISBN já existe na base de dados!', 'error')
        finally:
            conn.close()
    
    return render_template('livros/add_livro.html')

@livros_bp.route('/admin/livros/<int:id>/edit', methods=['GET', 'POST'])
def editar_livro(id):
    if session.get('user_type') != 'admin':
        flash('Acesso negado!', 'error')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect('db/biblioteca.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        categoria = request.form['categoria']
        isbn = request.form['isbn']
        descricao = request.form['descricao']
        
        # Get current book data
        c.execute("SELECT capa_url FROM livros WHERE id = ?", (id,))
        current_book = c.fetchone()
        capa_url = current_book[0] if current_book else None
        
        # Handle file upload
        if 'capa' in request.files:
            file = request.files['capa']
            if file and file.filename != '' and allowed_file(file.filename):
                # Delete old cover if exists
                if capa_url:
                    old_file_path = os.path.join('static', capa_url)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                filename = secure_filename(file.filename)
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file_path = os.path.join('static/images/covers', filename)
                file.save(file_path)
                capa_url = f'images/covers/{filename}'
        
        try:
            c.execute("""UPDATE livros SET titulo = ?, autor = ?, categoria = ?, 
                         isbn = ?, capa_url = ?, descricao = ? WHERE id = ?""",
                      (titulo, autor, categoria, isbn, capa_url, descricao, id))
            conn.commit()
            flash('Livro atualizado com sucesso!', 'success')
            return redirect(url_for('livros.ver_livros'))
        except sqlite3.IntegrityError:
            flash('ISBN já existe na base de dados!', 'error')
        finally:
            conn.close()
        
        return render_template('livros/editar_livro.html', livro=(id, titulo, autor, categoria, isbn, capa_url, '', '', descricao))
    
    # GET request
    c.execute("SELECT * FROM livros WHERE id = ?", (id,))
    livro = c.fetchone()
    conn.close()
    
    if not livro:
        flash('Livro não encontrado!', 'error')
        return redirect(url_for('livros.ver_livros'))
    
    return render_template('livros/editar_livro.html', livro=livro)

@livros_bp.route('/admin/livros/<int:id>/delete', methods=['POST'])
def delete_livro(id):
    if session.get('user_type') != 'admin':
        flash('Acesso negado!', 'error')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect('db/biblioteca.db')
    c = conn.cursor()
    
    # Check if book has active loans
    c.execute("SELECT COUNT(*) FROM emprestimos WHERE id_livro = ? AND status = 'ativo'", (id,))
    active_loans = c.fetchone()[0]
    
    if active_loans > 0:
        flash('Não é possível eliminar este livro pois tem empréstimos ativos!', 'error')
        conn.close()
        return redirect(url_for('livros.ver_livros'))
    
    # Get book cover to delete file
    c.execute("SELECT capa_url FROM livros WHERE id = ?", (id,))
    book = c.fetchone()
    
    if book and book[0]:
        cover_path = os.path.join('static', book[0])
        if os.path.exists(cover_path):
            os.remove(cover_path)
    
    # Delete book
    c.execute("DELETE FROM livros WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    
    flash('Livro eliminado com sucesso!', 'success')
    return redirect(url_for('livros.ver_livros')) 