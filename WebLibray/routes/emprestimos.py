from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from datetime import datetime, timedelta

emprestimos_bp = Blueprint('emprestimos', __name__)

@emprestimos_bp.route('/emprestimos')
def ver_emprestimos():
    user_type = session.get('user_type')
    user_id = session.get('user_id')
    
    conn = sqlite3.connect('db/biblioteca.db')
    c = conn.cursor()
    
    if user_type == 'admin':
        # Admin sees all loans
        status_filter = request.args.get('status', 'todos')
        
        query = """SELECT e.*, l.titulo, l.autor, u.nome 
                   FROM emprestimos e 
                   JOIN livros l ON e.id_livro = l.id 
                   JOIN utilizadores u ON e.id_utilizador = u.id"""
        
        params = []
        if status_filter != 'todos':
            query += " WHERE e.status = ?"
            params.append(status_filter)
        
        query += " ORDER BY e.data_emprestimo DESC"
        
        c.execute(query, params)
        emprestimos = c.fetchall()
        
        conn.close()
        return render_template('emprestimos/ver_emprestimos.html', 
                              emprestimos=emprestimos, 
                              is_admin=True,
                              status_filter=status_filter)
    
    else:
        # Students/Professors see only their loans
        c.execute("""SELECT e.*, l.titulo, l.autor, l.capa_url 
                     FROM emprestimos e 
                     JOIN livros l ON e.id_livro = l.id 
                     WHERE e.id_utilizador = ? 
                     ORDER BY e.data_emprestimo DESC""", (user_id,))
        emprestimos = c.fetchall()
        
        conn.close()
        return render_template('emprestimos/ver_emprestimos.html', 
                              emprestimos=emprestimos, 
                              is_admin=False)

@emprestimos_bp.route('/emprestimos/solicitar/<int:livro_id>', methods=['POST'])
def solicitar_emprestimo(livro_id):
    if session.get('user_type') not in ['aluno', 'professor']:
        flash('Acesso negado!', 'error')
        return redirect(url_for('livros.ver_livros'))
    
    user_id = session.get('user_id')
    
    conn = sqlite3.connect('db/biblioteca.db')
    c = conn.cursor()
    
    # Check if book is available
    c.execute("SELECT * FROM livros WHERE id = ? AND status = 'disponivel'", (livro_id,))
    livro = c.fetchone()
    
    if not livro:
        flash('Livro não disponível para empréstimo!', 'error')
        conn.close()
        return redirect(url_for('livros.detalhes_livro', id=livro_id))
    
    # Check if user already has this book
    c.execute("SELECT * FROM emprestimos WHERE id_utilizador = ? AND id_livro = ? AND status = 'ativo'", 
              (user_id, livro_id))
    if c.fetchone():
        flash('Já tem este livro emprestado!', 'error')
        conn.close()
        return redirect(url_for('livros.detalhes_livro', id=livro_id))
    
    # Check user's loan limit (max 3 books)
    c.execute("SELECT COUNT(*) FROM emprestimos WHERE id_utilizador = ? AND status = 'ativo'", (user_id,))
    active_loans = c.fetchone()[0]
    
    if active_loans >= 3:
        flash('Limite de empréstimos atingido (máximo 3 livros)!', 'error')
        conn.close()
        return redirect(url_for('livros.detalhes_livro', id=livro_id))
    
    # Create loan (15 days loan period)
    data_devolucao = datetime.now() + timedelta(days=15)
    
    try:
        # Add loan
        c.execute("""INSERT INTO emprestimos (id_utilizador, id_livro, data_devolucao_prevista) 
                     VALUES (?, ?, ?)""", (user_id, livro_id, data_devolucao))
        
        # Update book status
        c.execute("UPDATE livros SET status = 'emprestado' WHERE id = ?", (livro_id,))
        
        conn.commit()
        flash('Empréstimo realizado com sucesso! Data de devolução: ' + 
              data_devolucao.strftime('%d/%m/%Y'), 'success')
    
    except Exception as e:
        conn.rollback()
        flash('Erro ao processar empréstimo!', 'error')
    
    finally:
        conn.close()
    
    return redirect(url_for('emprestimos.ver_emprestimos'))

@emprestimos_bp.route('/emprestimos/<int:emprestimo_id>/devolver', methods=['POST'])
def devolver_livro(emprestimo_id):
    user_type = session.get('user_type')
    user_id = session.get('user_id')
    
    conn = sqlite3.connect('db/biblioteca.db')
    c = conn.cursor()
    
    # Get loan details
    c.execute("SELECT * FROM emprestimos WHERE id = ?", (emprestimo_id,))
    emprestimo = c.fetchone()
    
    if not emprestimo:
        flash('Empréstimo não encontrado!', 'error')
        conn.close()
        return redirect(url_for('emprestimos.ver_emprestimos'))
    
    # Check permissions
    if user_type != 'admin' and emprestimo[1] != user_id:  # id_utilizador column
        flash('Não tem permissão para devolver este empréstimo!', 'error')
        conn.close()
        return redirect(url_for('emprestimos.ver_emprestimos'))
    
    if emprestimo[6] != 'ativo':  # status column
        flash('Este empréstimo já foi devolvido!', 'error')
        conn.close()
        return redirect(url_for('emprestimos.ver_emprestimos'))
    
    try:
        # Update loan
        c.execute("""UPDATE emprestimos 
                     SET status = 'devolvido', data_devolucao_real = CURRENT_TIMESTAMP 
                     WHERE id = ?""", (emprestimo_id,))
        
        # Update book status
        c.execute("UPDATE livros SET status = 'disponivel' WHERE id = ?", (emprestimo[2],))  # id_livro
        
        conn.commit()
        flash('Livro devolvido com sucesso!', 'success')
    
    except Exception as e:
        conn.rollback()
        flash('Erro ao processar devolução!', 'error')
    
    finally:
        conn.close()
    
    return redirect(url_for('emprestimos.ver_emprestimos'))

@emprestimos_bp.route('/api/emprestimos/stats')
def emprestimos_stats():
    if session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = sqlite3.connect('db/biblioteca.db')
    c = conn.cursor()
    
    # Get monthly loan statistics
    c.execute("""SELECT strftime('%Y-%m', data_emprestimo) as month, COUNT(*) as count
                 FROM emprestimos 
                 WHERE data_emprestimo >= date('now', '-12 months')
                 GROUP BY month 
                 ORDER BY month""")
    monthly_stats = c.fetchall()
    
    # Get overdue loans
    c.execute("""SELECT COUNT(*) FROM emprestimos 
                 WHERE status = 'ativo' AND data_devolucao_prevista < date('now')""")
    overdue_count = c.fetchone()[0]
    
    # Update overdue status
    c.execute("""UPDATE emprestimos 
                 SET status = 'atrasado' 
                 WHERE status = 'ativo' AND data_devolucao_prevista < date('now')""")
    conn.commit()
    
    # Get category statistics
    c.execute("""SELECT l.categoria, COUNT(*) as count
                 FROM emprestimos e
                 JOIN livros l ON e.id_livro = l.id
                 WHERE e.data_emprestimo >= date('now', '-3 months')
                 GROUP BY l.categoria
                 ORDER BY count DESC
                 LIMIT 5""")
    category_stats = c.fetchall()
    
    conn.close()
    
    return jsonify({
        'monthly_stats': monthly_stats,
        'overdue_count': overdue_count,
        'category_stats': category_stats
    })

@emprestimos_bp.route('/emprestimos/renovar/<int:emprestimo_id>', methods=['POST'])
def renovar_emprestimo(emprestimo_id):
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    
    conn = sqlite3.connect('db/biblioteca.db')
    c = conn.cursor()
    
    # Get loan details
    c.execute("SELECT * FROM emprestimos WHERE id = ?", (emprestimo_id,))
    emprestimo = c.fetchone()
    
    if not emprestimo:
        flash('Empréstimo não encontrado!', 'error')
        conn.close()
        return redirect(url_for('emprestimos.ver_emprestimos'))
    
    # Check permissions
    if user_type != 'admin' and emprestimo[1] != user_id:
        flash('Não tem permissão para renovar este empréstimo!', 'error')
        conn.close()
        return redirect(url_for('emprestimos.ver_emprestimos'))
    
    if emprestimo[6] != 'ativo':  # status
        flash('Apenas empréstimos ativos podem ser renovados!', 'error')
        conn.close()
        return redirect(url_for('emprestimos.ver_emprestimos'))
    
    # Check if already overdue
    data_devolucao_prevista = datetime.strptime(emprestimo[4], '%Y-%m-%d %H:%M:%S')
    if data_devolucao_prevista < datetime.now():
        flash('Não é possível renovar um empréstimo em atraso!', 'error')
        conn.close()
        return redirect(url_for('emprestimos.ver_emprestimos'))
    
    # Extend loan by 7 days
    nova_data = data_devolucao_prevista + timedelta(days=7)
    
    try:
        c.execute("UPDATE emprestimos SET data_devolucao_prevista = ? WHERE id = ?", 
                  (nova_data, emprestimo_id))
        conn.commit()
        flash(f'Empréstimo renovado até {nova_data.strftime("%d/%m/%Y")}!', 'success')
    
    except Exception as e:
        conn.rollback()
        flash('Erro ao renovar empréstimo!', 'error')
    
    finally:
        conn.close()
    
    return redirect(url_for('emprestimos.ver_emprestimos')) 