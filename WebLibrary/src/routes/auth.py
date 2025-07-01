from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.database import get_db_connection
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        
        with get_db_connection() as (conn, cursor):
            cursor.execute("SELECT * FROM utilizadores WHERE email = ?", (email,))
            user = cursor.fetchone()
        
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['nome']
                session['user_type'] = user['tipo']
                flash(f'Bem-vindo, {user["nome"]}!', 'success')
                return redirect(url_for('main.dashboard'))
            else:
                flash('Email ou password incorretos!', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        tipo = request.form.get('tipo', '')
        
        # Validation errors list
        errors = []
        
        # Validate name
        if not nome:
            errors.append('Nome é obrigatório.')
        elif len(nome) < 2:
            errors.append('Nome deve ter pelo menos 2 caracteres.')
        elif len(nome) > 100:
            errors.append('Nome muito longo (máximo 100 caracteres).')
        elif not nome.replace(' ', '').replace('-', '').replace("'", '').isalpha():
            errors.append('Nome deve conter apenas letras, espaços, hífens e apóstrofes.')
        
        # Validate email
        email_regex = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
        if not email:
            errors.append('Email é obrigatório.')
        elif not re.match(email_regex, email):
            errors.append('Formato de email inválido.')
        
        # Validate password
        if not password:
            errors.append('Password é obrigatória.')
        elif len(password) < 6:
            errors.append('Password deve ter pelo menos 6 caracteres.')
        elif len(password) > 128:
            errors.append('Password muito longa (máximo 128 caracteres).')
        
        # Validate confirm password
        if not confirm_password:
            errors.append('Confirmação de password é obrigatória.')
        elif password != confirm_password:
            errors.append('As passwords não coincidem.')
        
        # Validate user type
        valid_types = ['aluno', 'professor']  # Admin users should be created by existing admins
        if not tipo:
            errors.append('Tipo de utilizador é obrigatório.')
        elif tipo not in valid_types:
            errors.append('Tipo de utilizador inválido.')
        
        # Check if email already exists
        if not errors:  # Only check if no other errors
            with get_db_connection() as (conn, cursor):
                cursor.execute("SELECT id FROM utilizadores WHERE email = ?", (email,))
                if cursor.fetchone():
                    errors.append('Este email já está registado.')
        
        # If there are validation errors, return to form
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        # Create new user
        try:
            with get_db_connection() as (conn, cursor):
                hashed_password = generate_password_hash(password)
                cursor.execute("""INSERT INTO utilizadores (nome, email, password, tipo) 
                                 VALUES (?, ?, ?, ?)""",
                              (nome, email, hashed_password, tipo))
                conn.commit()
            
            flash('Registo efetuado com sucesso! Pode agora fazer login.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            flash('Erro interno. Tente novamente mais tarde.', 'error')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/check-email', methods=['POST'])
def check_email():
    """API endpoint to check if email already exists"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'exists': False})
        
        with get_db_connection() as (conn, cursor):
            cursor.execute("SELECT id FROM utilizadores WHERE email = ?", (email,))
            exists = cursor.fetchone() is not None
            
        return jsonify({'exists': exists})
        
    except Exception as e:
        return jsonify({'exists': False}), 500

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logout efetuado com sucesso!', 'info')
    return redirect(url_for('main.index'))

