from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from src.models.database import get_db_connection
import os
from datetime import datetime
import mimetypes

documentos_bp = Blueprint('documentos', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def professor_or_admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') not in ['admin', 'professor']:
            flash('Acesso negado. Apenas professores e administradores podem aceder a esta funcionalidade.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Configurações de upload
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'xls'}
UPLOAD_FOLDER = 'documentos_estudo'

def allowed_file(filename):
    """Verificar se o tipo de ficheiro é permitido"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type_icon(filename):
    """Obter ícone baseado no tipo de ficheiro"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    icons = {
        'pdf': 'fas fa-file-pdf text-danger',
        'doc': 'fas fa-file-word text-primary',
        'docx': 'fas fa-file-word text-primary',
        'ppt': 'fas fa-file-powerpoint text-warning',
        'pptx': 'fas fa-file-powerpoint text-warning',
        'xlsx': 'fas fa-file-excel text-success',
        'xls': 'fas fa-file-excel text-success',
        'txt': 'fas fa-file-alt text-secondary',
        'png': 'fas fa-file-image text-info',
        'jpg': 'fas fa-file-image text-info',
        'jpeg': 'fas fa-file-image text-info',
        'gif': 'fas fa-file-image text-info'
    }
    return icons.get(ext, 'fas fa-file text-muted')

def get_disciplina_color(disciplina):
    """Obter cor baseada na disciplina"""
    colors = {
        'matemática': '#007bff',
        'português': '#28a745',
        'inglês': '#dc3545',
        'francês': '#6f42c1',
        'história': '#fd7e14',
        'geografia': '#20c997',
        'físico-química': '#e83e8c',
        'ciências naturais': '#6c757d',
        'educação física': '#17a2b8',
        'educação visual': '#ffc107',
        'educação tecnológica': '#343a40',
        'educação musical': '#e83e8c'
    }
    return colors.get(disciplina.lower(), '#6c757d')

def get_disciplina_class(disciplina):
    """Obter classe CSS baseada na disciplina"""
    classes = {
        'matemática': 'disciplina-matematica',
        'português': 'disciplina-portugues',
        'inglês': 'disciplina-ingles',
        'francês': 'disciplina-frances',
        'história': 'disciplina-historia',
        'geografia': 'disciplina-geografia',
        'físico-química': 'disciplina-fisico-quimica',
        'ciências naturais': 'disciplina-ciencias',
        'educação física': 'disciplina-educacao-fisica',
        'educação visual': 'disciplina-educacao-visual',
        'educação tecnológica': 'disciplina-educacao-tecnologica',
        'educação musical': 'disciplina-educacao-musical'
    }
    return classes.get(disciplina.lower(), 'disciplina-default')

@documentos_bp.route('/documentos')
@login_required
def ver_documentos():
    """Visualizar documentos de estudo com filtros"""
    ano_filter = request.args.get('ano', '')
    disciplina_filter = request.args.get('disciplina', '')
    search = request.args.get('search', '').strip()
    
    with get_db_connection() as (conn, cursor):
        # Query base
        query = """SELECT d.*, u.nome as autor_nome 
                   FROM documentos_estudo d 
                   JOIN utilizadores u ON d.autor_id = u.id 
                   WHERE 1=1"""
        params = []
        
        # Aplicar filtros
        if ano_filter:
            query += " AND d.ano_escolaridade = ?"
            params.append(ano_filter)
        
        if disciplina_filter:
            query += " AND LOWER(d.disciplina) = LOWER(?)"
            params.append(disciplina_filter)
        
        if search:
            query += " AND (LOWER(d.titulo) LIKE LOWER(?) OR LOWER(d.descricao) LIKE LOWER(?))"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
        
        query += " ORDER BY d.data_upload DESC"
        
        cursor.execute(query, params)
        documentos_raw = cursor.fetchall()
        
        # Converter data_upload para datetime se for string
        documentos = []
        for doc in documentos_raw:
            doc_dict = dict(doc)
            if isinstance(doc_dict['data_upload'], str):
                try:
                    doc_dict['data_upload'] = datetime.strptime(doc_dict['data_upload'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    try:
                        doc_dict['data_upload'] = datetime.strptime(doc_dict['data_upload'], '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        doc_dict['data_upload'] = datetime.now()
            documentos.append(doc_dict)
        
        # Obter lista de anos e disciplinas para os filtros
        cursor.execute("SELECT DISTINCT ano_escolaridade FROM documentos_estudo ORDER BY ano_escolaridade")
        anos = [row['ano_escolaridade'] for row in cursor.fetchall()]
        
        cursor.execute("SELECT DISTINCT disciplina FROM documentos_estudo ORDER BY disciplina")
        disciplinas = [row['disciplina'] for row in cursor.fetchall()]
    
    return render_template('documentos/ver_documentos.html',
                         documentos=documentos,
                         anos=anos,
                         disciplinas=disciplinas,
                         ano_filter=ano_filter,
                         disciplina_filter=disciplina_filter,
                         search=search,
                         get_file_type_icon=get_file_type_icon,
                         get_disciplina_color=get_disciplina_color,
                         get_disciplina_class=get_disciplina_class)

@documentos_bp.route('/documentos/upload', methods=['GET', 'POST'])
@professor_or_admin_required
def upload_documento():
    """Upload de novos documentos"""
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        descricao = request.form.get('descricao', '').strip()
        ano_escolaridade = request.form.get('ano_escolaridade', '')
        disciplina = request.form.get('disciplina', '').strip()
        tags = request.form.get('tags', '').strip()
        
        # Validações
        errors = []
        
        if not titulo:
            errors.append('Título é obrigatório.')
        elif len(titulo) > 255:
            errors.append('Título muito longo (máximo 255 caracteres).')
        
        if not ano_escolaridade:
            errors.append('Ano de escolaridade é obrigatório.')
        
        if not disciplina:
            errors.append('Disciplina é obrigatória.')
        elif len(disciplina) > 100:
            errors.append('Nome da disciplina muito longo (máximo 100 caracteres).')
        
        if descricao and len(descricao) > 1000:
            errors.append('Descrição muito longa (máximo 1000 caracteres).')
        
        # Verificar ficheiro
        if 'ficheiro' not in request.files:
            errors.append('Ficheiro é obrigatório.')
        else:
            file = request.files['ficheiro']
            if file.filename == '':
                errors.append('Nenhum ficheiro selecionado.')
            elif not allowed_file(file.filename):
                errors.append('Tipo de ficheiro não permitido.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            try:
                file = request.files['ficheiro']
                filename = secure_filename(file.filename)
                
                # Criar nome único para o ficheiro
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                unique_filename = timestamp + filename
                
                # Criar diretório se não existir
                upload_path = os.path.join('src', 'static', 'uploads', UPLOAD_FOLDER)
                os.makedirs(upload_path, exist_ok=True)
                
                # Guardar ficheiro
                file_path = os.path.join(upload_path, unique_filename)
                file.save(file_path)
                
                # Obter informações do ficheiro
                file_size = os.path.getsize(file_path)
                file_type = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                
                # Guardar na base de dados
                with get_db_connection() as (conn, cursor):
                    cursor.execute("""INSERT INTO documentos_estudo 
                                     (titulo, descricao, ano_escolaridade, disciplina, 
                                      ficheiro, tipo_ficheiro, tamanho_ficheiro, autor_id, tags) 
                                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                  (titulo, descricao, ano_escolaridade, disciplina,
                                   unique_filename, file_type, file_size, session['user_id'], tags))
                    conn.commit()
                
                flash(f'Documento "{titulo}" carregado com sucesso!', 'success')
                return redirect(url_for('documentos.ver_documentos'))
                
            except Exception as e:
                flash('Erro ao carregar documento. Tente novamente.', 'error')
    
    return render_template('documentos/upload_documento.html')

@documentos_bp.route('/documentos/<int:doc_id>/download')
@login_required
def download_documento(doc_id):
    """Download de documento"""
    with get_db_connection() as (conn, cursor):
        cursor.execute("SELECT * FROM documentos_estudo WHERE id = ?", (doc_id,))
        documento = cursor.fetchone()
        
        if not documento:
            flash('Documento não encontrado.', 'error')
            return redirect(url_for('documentos.ver_documentos'))
        
        # Incrementar contador de downloads
        cursor.execute("UPDATE documentos_estudo SET downloads = downloads + 1 WHERE id = ?", (doc_id,))
        conn.commit()
    
    try:
        upload_path = os.path.join('src', 'static', 'uploads', UPLOAD_FOLDER)
        return send_from_directory(upload_path, documento['ficheiro'], as_attachment=True)
    except FileNotFoundError:
        flash('Ficheiro não encontrado no servidor.', 'error')
        return redirect(url_for('documentos.ver_documentos'))

@documentos_bp.route('/documentos/<int:doc_id>/delete', methods=['POST'])
@professor_or_admin_required
def delete_documento(doc_id):
    """Eliminar documento"""
    with get_db_connection() as (conn, cursor):
        cursor.execute("SELECT * FROM documentos_estudo WHERE id = ?", (doc_id,))
        documento = cursor.fetchone()
        
        if not documento:
            flash('Documento não encontrado.', 'error')
            return redirect(url_for('documentos.ver_documentos'))
        
        # Verificar se o utilizador pode eliminar (autor ou admin)
        if documento['autor_id'] != session['user_id'] and session.get('user_type') != 'admin':
            flash('Não tem permissão para eliminar este documento.', 'error')
            return redirect(url_for('documentos.ver_documentos'))
        
        # Eliminar ficheiro do sistema
        try:
            file_path = os.path.join('src', 'static', 'uploads', UPLOAD_FOLDER, documento['ficheiro'])
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass  # Se não conseguir eliminar o ficheiro, continua
        
        # Eliminar da base de dados
        cursor.execute("DELETE FROM documentos_estudo WHERE id = ?", (doc_id,))
        conn.commit()
    
    flash('Documento eliminado com sucesso!', 'success')
    return redirect(url_for('documentos.ver_documentos'))

@documentos_bp.route('/documentos/meus')
@professor_or_admin_required
def meus_documentos():
    """Ver documentos do utilizador atual"""
    with get_db_connection() as (conn, cursor):
        cursor.execute("""SELECT * FROM documentos_estudo 
                         WHERE autor_id = ? 
                         ORDER BY data_upload DESC""", (session['user_id'],))
        documentos_raw = cursor.fetchall()
        
        # Converter data_upload para datetime se for string
        documentos = []
        for doc in documentos_raw:
            doc_dict = dict(doc)
            if isinstance(doc_dict['data_upload'], str):
                try:
                    doc_dict['data_upload'] = datetime.strptime(doc_dict['data_upload'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    try:
                        doc_dict['data_upload'] = datetime.strptime(doc_dict['data_upload'], '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        doc_dict['data_upload'] = datetime.now()
            documentos.append(doc_dict)
    
    return render_template('documentos/meus_documentos.html',
                         documentos=documentos,
                         get_file_type_icon=get_file_type_icon,
                         get_disciplina_color=get_disciplina_color,
                         get_disciplina_class=get_disciplina_class)

@documentos_bp.route('/api/documentos/stats')
@login_required
def documentos_stats():
    """API para estatísticas de documentos"""
    with get_db_connection() as (conn, cursor):
        # Total de documentos
        cursor.execute("SELECT COUNT(*) as total FROM documentos_estudo")
        total = cursor.fetchone()['total']
        
        # Documentos por disciplina
        cursor.execute("""SELECT disciplina, COUNT(*) as count 
                         FROM documentos_estudo 
                         GROUP BY disciplina 
                         ORDER BY count DESC""")
        por_disciplina = cursor.fetchall()
        
        # Documentos por ano
        cursor.execute("""SELECT ano_escolaridade, COUNT(*) as count 
                         FROM documentos_estudo 
                         GROUP BY ano_escolaridade 
                         ORDER BY ano_escolaridade""")
        por_ano = cursor.fetchall()
        
        # Downloads totais
        cursor.execute("SELECT SUM(downloads) as total_downloads FROM documentos_estudo")
        total_downloads = cursor.fetchone()['total_downloads'] or 0
    
    return jsonify({
        'total': total,
        'por_disciplina': [dict(row) for row in por_disciplina],
        'por_ano': [dict(row) for row in por_ano],
        'total_downloads': total_downloads
    }) 