from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from src.models.database import get_db_connection
from src.services.multas_service import MultasService
from datetime import datetime

multas_bp = Blueprint('multas', __name__)

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

# ===== ROTAS PARA UTILIZADORES =====

@multas_bp.route('/minhas-multas')
@login_required
def minhas_multas():
    """Ver multas do utilizador atual"""
    user_id = session.get('user_id')
    
    service = MultasService()
    multas = service.obter_multas_utilizador(user_id)
    
    # Calcular totais
    total_pendente = sum(float(m['valor_total']) for m in multas if m['status'] == 'pendente')
    total_pago = sum(float(m['valor_total']) for m in multas if m['status'] == 'paga')
    
    return render_template('multas/minhas_multas.html', 
                         multas=multas,
                         total_pendente=total_pendente,
                         total_pago=total_pago)

@multas_bp.route('/detalhes/<int:multa_id>')
@login_required
def detalhes_multa(multa_id):
    """Ver detalhes de uma multa específica"""
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    
    with get_db_connection() as (conn, cursor):
        # Verificar se a multa existe e se o utilizador pode vê-la
        if user_type == 'admin':
            query = """
                SELECT m.*, u.nome, u.email, l.titulo, l.autor,
                       e.data_emprestimo, e.data_devolucao_prevista, e.status as status_emprestimo
                FROM multas m
                JOIN utilizadores u ON m.id_utilizador = u.id
                JOIN emprestimos e ON m.id_emprestimo = e.id
                JOIN livros l ON e.id_livro = l.id
                WHERE m.id = ?
            """
            cursor.execute(query, (multa_id,))
        else:
            query = """
                SELECT m.*, u.nome, u.email, l.titulo, l.autor,
                       e.data_emprestimo, e.data_devolucao_prevista, e.status as status_emprestimo
                FROM multas m
                JOIN utilizadores u ON m.id_utilizador = u.id
                JOIN emprestimos e ON m.id_emprestimo = e.id
                JOIN livros l ON e.id_livro = l.id
                WHERE m.id = ? AND m.id_utilizador = ?
            """
            cursor.execute(query, (multa_id, user_id))
        
        multa = cursor.fetchone()
        
        if not multa:
            flash('Multa não encontrada.', 'error')
            return redirect(url_for('multas.minhas_multas'))
        
        # Obter histórico da multa
        cursor.execute("""
            SELECT h.*, u.nome as nome_usuario
            FROM historico_multas h
            LEFT JOIN utilizadores u ON h.usuario_acao = u.id
            WHERE h.id_multa = ?
            ORDER BY h.data_acao DESC
        """, (multa_id,))
        historico = cursor.fetchall()
        
        return render_template('multas/detalhes_multa.html', 
                             multa=multa, 
                             historico=historico,
                             is_admin=(user_type == 'admin'))

# ===== ROTAS PARA ADMINISTRADORES =====

@multas_bp.route('/admin/gestao')
@admin_required
def gestao_multas():
    """Página de gestão de multas para administradores"""
    # Filtros
    status_filter = request.args.get('status', '')
    user_filter = request.args.get('user', '')
    
    service = MultasService()
    
    with get_db_connection() as (conn, cursor):
        # Query base
        query = """
            SELECT m.*, u.nome, u.email, l.titulo, l.autor,
                   e.data_emprestimo, e.data_devolucao_prevista
            FROM multas m
            JOIN utilizadores u ON m.id_utilizador = u.id
            JOIN emprestimos e ON m.id_emprestimo = e.id
            JOIN livros l ON e.id_livro = l.id
            WHERE 1=1
        """
        params = []
        
        # Aplicar filtros
        if status_filter:
            query += " AND m.status = ?"
            params.append(status_filter)
        
        if user_filter:
            query += " AND u.nome LIKE ?"
            params.append(f"%{user_filter}%")
        
        query += " ORDER BY m.valor_total DESC, m.data_criacao DESC"
        
        cursor.execute(query, params)
        multas = cursor.fetchall()
        
        # Estatísticas
        cursor.execute("SELECT COUNT(*), SUM(valor_total) FROM multas WHERE status = 'pendente'")
        stats_pendente = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*), SUM(valor_total) FROM multas WHERE status = 'paga'")
        stats_paga = cursor.fetchone()
        
        estatisticas = {
            'pendentes': {
                'count': stats_pendente[0] or 0,
                'total': float(stats_pendente[1] or 0)
            },
            'pagas': {
                'count': stats_paga[0] or 0,
                'total': float(stats_paga[1] or 0)
            }
        }
    
    return render_template('multas/gestao_multas.html', 
                         multas=multas,
                         estatisticas=estatisticas,
                         status_filter=status_filter,
                         user_filter=user_filter)

@multas_bp.route('/admin/pagar/<int:multa_id>', methods=['POST'])
@admin_required
def pagar_multa(multa_id):
    """Marcar uma multa como paga"""
    admin_id = session.get('user_id')
    
    service = MultasService()
    sucesso = service.pagar_multa(multa_id, admin_id)
    
    if sucesso:
        flash('Multa marcada como paga com sucesso!', 'success')
    else:
        flash('Erro ao processar pagamento da multa.', 'error')
    
    return redirect(url_for('multas.gestao_multas'))

@multas_bp.route('/admin/cancelar/<int:multa_id>', methods=['POST'])
@admin_required
def cancelar_multa(multa_id):
    """Cancelar uma multa"""
    admin_id = session.get('user_id')
    observacoes = request.form.get('observacoes', '')
    
    with get_db_connection() as (conn, cursor):
        # Obter dados da multa
        cursor.execute("SELECT valor_total FROM multas WHERE id = ?", (multa_id,))
        resultado = cursor.fetchone()
        
        if not resultado:
            flash('Multa não encontrada.', 'error')
            return redirect(url_for('multas.gestao_multas'))
        
        valor = resultado['valor_total']
        
        # Cancelar multa
        cursor.execute("""
            UPDATE multas SET status = 'cancelada' WHERE id = ?
        """, (multa_id,))
        
        # Registrar no histórico
        cursor.execute("""
            INSERT INTO historico_multas (id_multa, acao, valor_anterior, usuario_acao, observacoes)
            VALUES (?, 'cancelada', ?, ?, ?)
        """, (multa_id, valor, admin_id, observacoes or 'Multa cancelada pelo administrador'))
        
        conn.commit()
    
    flash('Multa cancelada com sucesso!', 'success')
    return redirect(url_for('multas.gestao_multas'))

@multas_bp.route('/admin/processar-atrasos', methods=['POST'])
@admin_required
def processar_atrasos():
    """Executar processamento manual de atrasos"""
    try:
        service = MultasService()
        service.processar_atrasos_diarios()
        flash('Processamento de atrasos executado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao processar atrasos: {str(e)}', 'error')
    
    return redirect(url_for('multas.gestao_multas'))

# ===== API ENDPOINTS =====

@multas_bp.route('/api/estatisticas')
@admin_required
def api_estatisticas():
    """API para obter estatísticas de multas"""
    with get_db_connection() as (conn, cursor):
        # Multas por status
        cursor.execute("""
            SELECT status, COUNT(*) as count, SUM(valor_total) as total
            FROM multas
            GROUP BY status
        """)
        stats_status = cursor.fetchall()
        
        # Multas por mês (últimos 6 meses)
        cursor.execute("""
            SELECT strftime('%Y-%m', data_criacao) as mes, 
                   COUNT(*) as count, 
                   SUM(valor_total) as total
            FROM multas
            WHERE data_criacao >= date('now', '-6 months')
            GROUP BY strftime('%Y-%m', data_criacao)
            ORDER BY mes
        """)
        stats_mensal = cursor.fetchall()
        
        # Top utilizadores com mais multas
        cursor.execute("""
            SELECT u.nome, COUNT(*) as count, SUM(m.valor_total) as total
            FROM multas m
            JOIN utilizadores u ON m.id_utilizador = u.id
            WHERE m.status = 'pendente'
            GROUP BY u.id, u.nome
            ORDER BY total DESC
            LIMIT 5
        """)
        top_utilizadores = cursor.fetchall()
    
    return jsonify({
        'status_stats': [dict(row) for row in stats_status],
        'monthly_stats': [dict(row) for row in stats_mensal],
        'top_users': [dict(row) for row in top_utilizadores]
    }) 