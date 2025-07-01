import sqlite3
import os
from contextlib import contextmanager
from flask import current_app
from werkzeug.security import generate_password_hash

@contextmanager
def get_db_connection():
    """
    Context manager para gerir conexões à base de dados SQLite.
    
    Yields:
        tuple: (connection, cursor) - Objetos de conexão e cursor da base de dados
        
    Example:
        with get_db_connection() as (conn, cursor):
            cursor.execute("SELECT * FROM utilizadores")
            users = cursor.fetchall()
            conn.commit()  # Para operações de escrita
    """
    conn = None
    try:
        # Obter o caminho da base de dados das configurações da aplicação
        db_path = current_app.config['DATABASE_PATH']
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        
        # Configurar row_factory para acesso por nome das colunas (ex: user['email'])
        conn.row_factory = sqlite3.Row
        
        cursor = conn.cursor()
        yield conn, cursor
        
    except Exception as e:
        # Em caso de erro, fazer rollback se a conexão existe
        if conn:
            conn.rollback()
        raise e
        
    finally:
        # Garantir que a conexão é sempre fechada
        if conn:
            conn.close()

def init_db():
    """Inicializar a base de dados com as tabelas necessárias"""
    
    # Use direct connection since app context might not be available yet
    db_path = current_app.config['DATABASE_PATH']
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Tabela de utilizadores
        cursor.execute('''CREATE TABLE IF NOT EXISTS utilizadores (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         nome TEXT NOT NULL,
                         email TEXT UNIQUE NOT NULL,
                         password TEXT NOT NULL,
                         tipo TEXT NOT NULL CHECK(tipo IN ('admin', 'aluno', 'professor')),
                         data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                         telefone TEXT,
                         data_nascimento DATE,
                         endereco TEXT,
                         biografia TEXT,
                         notificacoes_email INTEGER DEFAULT 1,
                         lembretes_devolucao INTEGER DEFAULT 1
                         )''')
        
        # Tabela de livros
        cursor.execute('''CREATE TABLE IF NOT EXISTS livros (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         titulo TEXT NOT NULL,
                         autor TEXT NOT NULL,
                         categoria TEXT NOT NULL,
                         isbn TEXT UNIQUE,
                         capa_url TEXT,
                         status TEXT DEFAULT 'disponivel' CHECK(status IN ('disponivel', 'emprestado')),
                         data_adicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                         descricao TEXT,
                         ano_publicacao INTEGER,
                         editora TEXT,
                         paginas INTEGER,
                         idioma TEXT
                         )''')
        
        # Tabela de empréstimos
        cursor.execute('''CREATE TABLE IF NOT EXISTS emprestimos (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         id_utilizador INTEGER NOT NULL,
                         id_livro INTEGER NOT NULL,
                         data_emprestimo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                         data_devolucao_prevista TIMESTAMP NOT NULL,
                         data_devolucao_real TIMESTAMP,
                         status TEXT DEFAULT 'ativo' CHECK(status IN ('ativo', 'devolvido', 'atrasado')),
                         renovado INTEGER DEFAULT 0,
                         FOREIGN KEY (id_utilizador) REFERENCES utilizadores (id),
                         FOREIGN KEY (id_livro) REFERENCES livros (id)
                         )''')
                         
        # Tabela de documentos de estudo
        cursor.execute('''CREATE TABLE IF NOT EXISTS documentos_estudo (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         titulo TEXT NOT NULL,
                         descricao TEXT,
                         ano_escolaridade TEXT NOT NULL,
                         disciplina TEXT NOT NULL,
                         ficheiro TEXT NOT NULL,
                         tipo_ficheiro TEXT NOT NULL,
                         tamanho_ficheiro INTEGER,
                         autor_id INTEGER NOT NULL,
                         data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                         tags TEXT,
                         downloads INTEGER DEFAULT 0,
                         FOREIGN KEY (autor_id) REFERENCES utilizadores (id)
                         )''')

        # Tabela de multas por atraso
        cursor.execute('''CREATE TABLE IF NOT EXISTS multas (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         id_emprestimo INTEGER NOT NULL,
                         id_utilizador INTEGER NOT NULL,
                         valor_total DECIMAL(10,2) DEFAULT 0.00,
                         dias_atraso INTEGER DEFAULT 0,
                         data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                         data_pagamento TIMESTAMP,
                         status TEXT DEFAULT 'pendente' CHECK(status IN ('pendente', 'paga', 'cancelada')),
                         observacoes TEXT,
                         FOREIGN KEY (id_emprestimo) REFERENCES emprestimos (id),
                         FOREIGN KEY (id_utilizador) REFERENCES utilizadores (id)
                         )''')

        # Tabela de notificações de atraso
        cursor.execute('''CREATE TABLE IF NOT EXISTS notificacoes_atraso (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         id_emprestimo INTEGER NOT NULL,
                         id_utilizador INTEGER NOT NULL,
                         tipo_notificacao TEXT NOT NULL CHECK(tipo_notificacao IN ('email', 'sistema')),
                         conteudo TEXT NOT NULL,
                         data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                         email_enviado INTEGER DEFAULT 0,
                         dias_atraso INTEGER NOT NULL,
                         FOREIGN KEY (id_emprestimo) REFERENCES emprestimos (id),
                         FOREIGN KEY (id_utilizador) REFERENCES utilizadores (id)
                         )''')

        # Tabela de histórico de multas (para auditoria)
        cursor.execute('''CREATE TABLE IF NOT EXISTS historico_multas (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         id_multa INTEGER NOT NULL,
                         acao TEXT NOT NULL CHECK(acao IN ('criada', 'atualizada', 'paga', 'cancelada')),
                         valor_anterior DECIMAL(10,2),
                         valor_novo DECIMAL(10,2),
                         usuario_acao INTEGER,
                         data_acao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                         observacoes TEXT,
                         FOREIGN KEY (id_multa) REFERENCES multas (id),
                         FOREIGN KEY (usuario_acao) REFERENCES utilizadores (id)
                         )''')
        
        # Criar utilizador admin padrão se não existir
        cursor.execute("SELECT * FROM utilizadores WHERE email = ?", 
                      (current_app.config['DEFAULT_ADMIN_EMAIL'],))
        if not cursor.fetchone():
            admin_password = generate_password_hash(current_app.config['DEFAULT_ADMIN_PASSWORD'])
            cursor.execute("""INSERT INTO utilizadores (nome, email, password, tipo) 
                             VALUES (?, ?, ?, ?)""",
                          (current_app.config['DEFAULT_ADMIN_NAME'], 
                           current_app.config['DEFAULT_ADMIN_EMAIL'], 
                           admin_password, 'admin'))
        
        # Inserir alguns livros de exemplo se a tabela estiver vazia
        cursor.execute("SELECT COUNT(*) FROM livros")
        if cursor.fetchone()[0] == 0:
            livros_exemplo = [
                ('O Alquimista', 'Paulo Coelho', 'Ficção', '9788576651017', None, 'disponivel', 
                 'Uma fábula sobre seguir os sonhos e encontrar o próprio destino.', 1988, 'Planeta', 163, 'Português'),
                ('1984', 'George Orwell', 'Ficção Científica', '9780451524935', None, 'disponivel',
                 'Um romance distópico sobre totalitarismo e vigilância.', 1949, 'Secker & Warburg', 328, 'Inglês'),
                ('Dom Casmurro', 'Machado de Assis', 'Literatura Clássica', '9788525406958', None, 'disponivel',
                 'Romance sobre ciúme e dúvida na sociedade carioca do século XIX.', 1899, 'Garnier', 208, 'Português'),
                ('O Pequeno Príncipe', 'Antoine de Saint-Exupéry', 'Infantil', '9788595081413', None, 'disponivel',
                 'Uma história poética sobre amizade, amor e perda.', 1943, 'Reynal & Hitchcock', 96, 'Francês'),
                ('Sapiens', 'Yuval Noah Harari', 'História', '9780062316097', None, 'disponivel',
                 'Uma breve história da humanidade desde a Idade da Pedra até a era digital.', 2011, 'Harvill Secker', 443, 'Inglês'),
                ('A Arte da Guerra', 'Sun Tzu', 'Filosofia', '9788576843726', None, 'disponivel',
                 'Tratado militar sobre estratégia e táticas de guerra.', -500, 'Desconhecida', 112, 'Chinês'),
            ]
            
            for livro in livros_exemplo:
                cursor.execute("""INSERT INTO livros 
                                 (titulo, autor, categoria, isbn, capa_url, status, descricao, 
                                  ano_publicacao, editora, paginas, idioma) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", livro)
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_db_path():
    """
    Função auxiliar para obter o caminho da base de dados.
    
    Returns:
        str: Caminho para o ficheiro da base de dados
    """
    return current_app.config['DATABASE_PATH']

