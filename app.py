from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime, timedelta
from functools import wraps
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'biblioteca_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'static/images/covers'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect('db/biblioteca.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS utilizadores (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 nome TEXT NOT NULL,
                 email TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL,
                 tipo TEXT NOT NULL CHECK(tipo IN ('admin', 'aluno', 'professor')),
                 data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                 )''')
    
    # Books table
    c.execute('''CREATE TABLE IF NOT EXISTS livros (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 titulo TEXT NOT NULL,
                 autor TEXT NOT NULL,
                 categoria TEXT NOT NULL,
                 isbn TEXT UNIQUE,
                 capa_url TEXT,
                 status TEXT DEFAULT 'disponivel' CHECK(status IN ('disponivel', 'emprestado')),
                 data_adicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 descricao TEXT
                 )''')
    
    # Loans table
    c.execute('''CREATE TABLE IF NOT EXISTS emprestimos (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 id_utilizador INTEGER NOT NULL,
                 id_livro INTEGER NOT NULL,
                 data_emprestimo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 data_devolucao_prevista TIMESTAMP NOT NULL,
                 data_devolucao_real TIMESTAMP,
                 status TEXT DEFAULT 'ativo' CHECK(status IN ('ativo', 'devolvido', 'atrasado')),
                 FOREIGN KEY (id_utilizador) REFERENCES utilizadores (id),
                 FOREIGN KEY (id_livro) REFERENCES livros (id)
                 )''')
    
    # Create admin user if not exists
    c.execute("SELECT * FROM utilizadores WHERE email = 'admin@biblioteca.com'")
    if not c.fetchone():
        admin_password = generate_password_hash('admin123')
        c.execute("INSERT INTO utilizadores (nome, email, password, tipo) VALUES (?, ?, ?, ?)",
                  ('Administrador', 'admin@biblioteca.com', admin_password, 'admin'))
    
    conn.commit()
    conn.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'admin':
            flash('Acesso negado. Apenas administradores podem aceder a esta página.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('db/biblioteca.db')
        c = conn.cursor()
        c.execute("SELECT * FROM utilizadores WHERE email = ?", (email,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_type'] = user[4]
            flash(f'Bem-vindo, {user[1]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou password incorretos!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        tipo = request.form['tipo']
        
        if password != confirm_password:
            flash('As passwords não coincidem!', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('A password deve ter pelo menos 6 caracteres!', 'error')
            return render_template('register.html')
        
        conn = sqlite3.connect('db/biblioteca.db')
        c = conn.cursor()
        
        # Check if email already exists
        c.execute("SELECT * FROM utilizadores WHERE email = ?", (email,))
        if c.fetchone():
            flash('Este email já está registado!', 'error')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        hashed_password = generate_password_hash(password)
        c.execute("INSERT INTO utilizadores (nome, email, password, tipo) VALUES (?, ?, ?, ?)",
                  (nome, email, hashed_password, tipo))
        conn.commit()
        conn.close()
        
        flash('Registo efetuado com sucesso! Pode agora fazer login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_type = session.get('user_type')
    
    conn = sqlite3.connect('db/biblioteca.db')
    c = conn.cursor()
    
    if user_type == 'admin':
        # Admin statistics
        c.execute("SELECT COUNT(*) FROM livros")
        total_livros = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM utilizadores")
        total_utilizadores = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM emprestimos WHERE status = 'ativo'")
        emprestimos_ativos = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM emprestimos WHERE status = 'atrasado'")
        emprestimos_atrasados = c.fetchone()[0]
        
        conn.close()
        
        return render_template('dashboard_admin.html', 
                             total_livros=total_livros,
                             total_utilizadores=total_utilizadores,
                             emprestimos_ativos=emprestimos_ativos,
                             emprestimos_atrasados=emprestimos_atrasados)
    
    else:
        # Student/Professor dashboard
        user_id = session.get('user_id')
        
        # Get user's active loans
        c.execute("""SELECT e.*, l.titulo, l.autor, l.capa_url 
                     FROM emprestimos e 
                     JOIN livros l ON e.id_livro = l.id 
                     WHERE e.id_utilizador = ? AND e.status = 'ativo'
                     ORDER BY e.data_emprestimo DESC""", (user_id,))
        emprestimos_ativos = c.fetchall()
        
        # Get recently added books
        c.execute("SELECT * FROM livros WHERE status = 'disponivel' ORDER BY data_adicao DESC LIMIT 6")
        livros_recentes = c.fetchall()
        
        conn.close()
        
        template_name = f'dashboard_{user_type}.html'
        return render_template(template_name, 
                             emprestimos_ativos=emprestimos_ativos,
                             livros_recentes=livros_recentes)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout efetuado com sucesso!', 'success')
    return redirect(url_for('login'))

# Register blueprints
from routes.livros import livros_bp
from routes.emprestimos import emprestimos_bp
from routes.admin import admin_bp
from routes.profile import profile_bp

app.register_blueprint(livros_bp)
app.register_blueprint(emprestimos_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(profile_bp)

if __name__ == '__main__':
    # Create database directory if it doesn't exist
    os.makedirs('db', exist_ok=True)
    init_db()
    app.run(debug=True) 