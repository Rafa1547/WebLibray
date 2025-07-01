import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, session, redirect, url_for, render_template, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import secrets

# Import models and routes
from src.models.database import init_db, get_db_connection
from src.routes.auth import auth_bp
from src.routes.main import main_bp
from src.routes.books import books_bp
from src.routes.loans import loans_bp
from src.routes.users import users_bp
from src.routes.admin import admin_bp
from src.routes.documentos import documentos_bp
from src.routes.multas import multas_bp

app = Flask(__name__, 
           static_folder=os.path.join(os.path.dirname(__file__), 'static'),
           template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config['DATABASE_PATH'] = os.path.join(os.path.dirname(__file__), 'database', 'weblibrary.db')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'images', 'covers')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure uploads directory for documents exists
uploads_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'documentos_estudo')
os.makedirs(uploads_dir, exist_ok=True)

# Default admin credentials
app.config['DEFAULT_ADMIN_EMAIL'] = 'admin@weblibrary.com'
app.config['DEFAULT_ADMIN_PASSWORD'] = 'admin123'
app.config['DEFAULT_ADMIN_NAME'] = 'Administrador'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
with app.app_context():
    init_db()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(main_bp)
app.register_blueprint(books_bp, url_prefix='/books')
app.register_blueprint(loans_bp, url_prefix='/loans')
app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(documentos_bp)
app.register_blueprint(multas_bp, url_prefix='/multas')

# Helper functions
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'admin':
            flash('Acesso negado. Apenas administradores podem aceder a esta página.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Error handlers
@app.errorhandler(403)
def access_forbidden(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

# Template filters
@app.template_filter('datetime')
def datetime_filter(value, format='%d/%m/%Y %H:%M'):
    """
    Filtro robusto para formatação de datas que lida com strings, objetos datetime e None
    """
    if value is None:
        return 'N/A'
    
    if isinstance(value, str):
        # Tentar diferentes formatos de string de data
        formats_to_try = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%d',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y',
        ]
        
        for fmt in formats_to_try:
            try:
                value = datetime.strptime(value, fmt)
                break
            except (ValueError, TypeError):
                continue
        else:
            # Se nenhum formato funcionou, retornar a string original
            return str(value)
    
    # Se value é um objeto datetime válido
    if isinstance(value, datetime):
        try:
            return value.strftime(format)
        except (ValueError, TypeError):
            return str(value)
    
    # Fallback para outros tipos
    return str(value) if value else 'N/A'

# Template globals
@app.template_global()
def get_current_user():
    if 'user_id' in session:
        with get_db_connection() as (conn, cursor):
            cursor.execute("SELECT * FROM utilizadores WHERE id = ?", (session['user_id'],))
            return cursor.fetchone()
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
