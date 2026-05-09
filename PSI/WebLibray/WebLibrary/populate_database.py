#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para popular a base de dados da WebLibrary com dados de teste.
"""

import sqlite3
import os
import sys
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import random

def get_db_path():
    """Retorna o caminho da base de dados"""
    return os.path.join(os.path.dirname(__file__), 'src', 'database', 'weblibrary.db')

def create_connection():
    """Cria conexão com a base de dados"""
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def insert_users(conn):
    """Inserir utilizadores de teste"""
    print("📝 Inserindo utilizadores...")
    
    users_data = [
        # Admins
        ('Ana Silva', 'ana.silva@biblioteca.pt', 'admin123', 'admin'),
        ('Carlos Santos', 'carlos.santos@biblioteca.pt', 'admin123', 'admin'),
        
        # Professores
        ('Maria João Pereira', 'maria.pereira@escola.pt', 'prof123', 'professor'),
        ('João Manuel Costa', 'joao.costa@escola.pt', 'prof123', 'professor'),
        ('Teresa Rodrigues', 'teresa.rodrigues@escola.pt', 'prof123', 'professor'),
        
        # Alunos
        ('Pedro Gonçalves', 'pedro.goncalves@aluno.pt', 'aluno123', 'aluno'),
        ('Sofia Carvalho', 'sofia.carvalho@aluno.pt', 'aluno123', 'aluno'),
        ('Miguel Ferreira', 'miguel.ferreira@aluno.pt', 'aluno123', 'aluno'),
        ('Catarina Lopes', 'catarina.lopes@aluno.pt', 'aluno123', 'aluno'),
        ('Bruno Almeida', 'bruno.almeida@aluno.pt', 'aluno123', 'aluno'),
    ]
    
    cursor = conn.cursor()
    
    for user_data in users_data:
        nome, email, password, tipo = user_data
        hashed_password = generate_password_hash(password)
        
        try:
            cursor.execute("""
                INSERT INTO utilizadores (nome, email, password, tipo)
                VALUES (?, ?, ?, ?)
            """, (nome, email, hashed_password, tipo))
            print(f"  ✅ Utilizador criado: {nome} ({tipo})")
        except sqlite3.IntegrityError:
            print(f"  ⚠️  Utilizador já existe: {email}")
    
    conn.commit()
    print(f"✅ {len(users_data)} utilizadores processados!")

def insert_books(conn):
    """Inserir livros de teste"""
    print("\n📚 Inserindo livros...")
    
    books_data = [
        ('Os Maias', 'Eça de Queirós', 'Literatura Clássica', '9789722036726', 'disponivel', 
         'Romance que retrata a sociedade portuguesa do século XIX.', 1888, 'Livros do Brasil', 592, 'Português'),
        
        ('Memorial do Convento', 'José Saramago', 'Literatura Clássica', '9789722018559', 'disponivel',
         'Romance histórico sobre a construção do Convento de Mafra.', 1982, 'Editorial Caminho', 356, 'Português'),
         
        ('Dom Quixote', 'Miguel de Cervantes', 'Literatura Clássica', '9780060934347', 'disponivel',
         'Obra-prima da literatura espanhola.', 1605, 'Publicações Dom Quixote', 863, 'Espanhol'),
         
        ('Cem Anos de Solidão', 'Gabriel García Márquez', 'Literatura Clássica', '9788535909147', 'disponivel',
         'Saga da família Buendía em Macondo.', 1967, 'Editorial Sudamericana', 471, 'Espanhol'),
         
        ('Duna', 'Frank Herbert', 'Ficção Científica', '9788576573486', 'disponivel',
         'Épico de ficção científica no planeta Arrakis.', 1965, 'Aleph', 688, 'Inglês'),
         
        ('Foundation', 'Isaac Asimov', 'Ficção Científica', '9780553293357', 'disponivel',
         'Primeiro livro da série Foundation.', 1951, 'Aleph', 244, 'Inglês'),
         
        ('História de Portugal', 'José Hermano Saraiva', 'História', '9789722414814', 'disponivel',
         'Síntese da história portuguesa.', 1993, 'Publicações Europa-América', 512, 'Português'),
         
        ('Sapiens', 'Yuval Noah Harari', 'História', '9788525432681', 'disponivel',
         'Uma breve história da humanidade.', 2011, 'L&PM Editores', 464, 'Hebraico'),
         
        ('Uma Breve História do Tempo', 'Stephen Hawking', 'Ciência', '9788580570267', 'disponivel',
         'Os mistérios do universo explicados.', 1988, 'Bantam Books', 256, 'Inglês'),
         
        ('Cosmos', 'Carl Sagan', 'Ciência', '9788535906769', 'disponivel',
         'Jornada através do cosmos.', 1980, 'Companhia das Letras', 432, 'Inglês'),
         
        ('A República', 'Platão', 'Filosofia', '9789722041614', 'disponivel',
         'Diálogo sobre justiça e a cidade ideal.', -380, 'Fundação Calouste Gulbenkian', 512, 'Grego'),
         
        ('Harry Potter e a Pedra Filosofal', 'J.K. Rowling', 'Infantil', '9788532511010', 'disponivel',
         'Primeiro livro da saga Harry Potter.', 1997, 'Rocco', 264, 'Inglês'),
         
        ('Percy Jackson - O Ladrão de Raios', 'Rick Riordan', 'Infantil', '9788598078355', 'disponivel',
         'Aventuras na mitologia grega moderna.', 2005, 'Intrínseca', 377, 'Inglês'),
         
        ('Mensagem', 'Fernando Pessoa', 'Literatura Clássica', '9789722414821', 'disponivel',
         'Único livro de poemas publicado por Pessoa.', 1934, 'Ática', 96, 'Português'),
         
        ('Steve Jobs', 'Walter Isaacson', 'Biografia', '9788535918304', 'disponivel',
         'Biografia do cofundador da Apple.', 2011, 'Companhia das Letras', 656, 'Inglês'),
         
        # Exemplos das novas categorias
        ('Psicologia: Uma Nova Síntese', 'Michael Eysenck', 'Psicologia', '9788582715123', 'disponivel',
         'Introdução abrangente à psicologia moderna.', 2017, 'Artmed', 896, 'Inglês'),
         
        ('Anatomia Humana', 'Frank H. Netter', 'Medicina e Saúde', '9788535287134', 'disponivel',
         'Atlas de anatomia humana com ilustrações detalhadas.', 2019, 'Elsevier', 672, 'Inglês'),
         
        ('Direito Constitucional', 'Pedro Lenza', 'Direito', '9788547231156', 'disponivel',
         'Manual de direito constitucional brasileiro.', 2020, 'Saraiva', 1584, 'Português'),
         
        ('Princípios de Economia', 'N. Gregory Mankiw', 'Economia', '9788522127030', 'disponivel',
         'Fundamentos da economia moderna.', 2020, 'Cengage Learning', 768, 'Inglês'),
         
        ('Pedagogia da Autonomia', 'Paulo Freire', 'Educação', '9788577531639', 'disponivel',
         'Saberes necessários à prática educativa.', 1996, 'Paz e Terra', 144, 'Português'),
         
        ('Geografia: O Mundo Subdesenvolvido', 'Yves Lacoste', 'Geografia', '9788571394734', 'disponivel',
         'Análise geográfica do desenvolvimento mundial.', 1990, 'Difel', 284, 'Francês'),
         
        ('Cálculo Volume 1', 'James Stewart', 'Matemática', '9788522112593', 'disponivel',
         'Fundamentos do cálculo diferencial e integral.', 2016, 'Cengage Learning', 1024, 'Inglês'),
         
        ('Estruturas de Dados e Algoritmos', 'Michael Goodrich', 'Tecnologia', '9788582603475', 'disponivel',
         'Fundamentos de programação e algoritmos.', 2013, 'Bookman', 720, 'Inglês'),
         
        ('Dicionário Oxford Inglês-Português', 'Oxford University Press', 'Línguas', '9780194424691', 'disponivel',
         'Dicionário bilíngue completo.', 2018, 'Oxford', 832, 'Inglês'),
         
        ('História das Religiões', 'Mircea Eliade', 'Religião', '9788533622647', 'disponivel',
         'Estudo comparativo das principais religiões.', 2010, 'Martins Fontes', 496, 'Francês'),
         
        ('Como Fazer Amigos e Influenciar Pessoas', 'Dale Carnegie', 'Autoajuda', '9788504018028', 'disponivel',
         'Clássico do desenvolvimento pessoal.', 1936, 'Companhia Editora Nacional', 312, 'Inglês'),
         
        ('Sabores do Brasil', 'Ana Luiza Trajano', 'Culinária', '9788541300742', 'disponivel',
         'Receitas tradicionais da culinária brasileira.', 2015, 'Melhoramentos', 256, 'Português'),
         
                 ('Manual de Educação Física', 'José Carlos Barbanti', 'Desporto', '9788520439234', 'disponivel',
          'Fundamentos do treino e exercício físico.', 2010, 'Manole', 448, 'Português'),
    ]
    
    cursor = conn.cursor()
    
    for book_data in books_data:
        titulo, autor, categoria, isbn, status, descricao, ano_publicacao, editora, paginas, idioma = book_data
        
        try:
            cursor.execute("""
                INSERT INTO livros (titulo, autor, categoria, isbn, status, descricao, ano_publicacao, editora, paginas, idioma)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (titulo, autor, categoria, isbn, status, descricao, ano_publicacao, editora, paginas, idioma))
            print(f"  ✅ Livro criado: {titulo} - {autor}")
        except sqlite3.IntegrityError:
            print(f"  ⚠️  Livro já existe: {isbn}")
    
    conn.commit()
    print(f"✅ {len(books_data)} livros processados!")

def insert_loans(conn):
    """Inserir empréstimos de teste"""
    print("\n📋 Inserindo empréstimos...")
    
    cursor = conn.cursor()
    
    # Obter utilizadores não-admin
    cursor.execute("SELECT id FROM utilizadores WHERE tipo != 'admin'")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    # Obter livros disponíveis
    cursor.execute("SELECT id FROM livros WHERE status = 'disponivel'")
    book_ids = [row[0] for row in cursor.fetchall()]
    
    if not user_ids or not book_ids:
        print("⚠️  Sem utilizadores ou livros disponíveis")
        return
    
    # Criar 10 empréstimos ativos
    for i in range(min(10, len(user_ids), len(book_ids))):
        user_id = user_ids[i % len(user_ids)]
        book_id = book_ids[i]
        
        days_ago = random.randint(1, 30)
        data_emprestimo = datetime.now() - timedelta(days=days_ago)
        data_devolucao_prevista = data_emprestimo + timedelta(days=15)
        
        try:
            cursor.execute("""
                INSERT INTO emprestimos (id_utilizador, id_livro, data_emprestimo, data_devolucao_prevista, status)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, book_id, data_emprestimo, data_devolucao_prevista, 'ativo'))
            
            cursor.execute("UPDATE livros SET status = 'emprestado' WHERE id = ?", (book_id,))
            print(f"  ✅ Empréstimo ativo: Utilizador {user_id}, Livro {book_id}")
        except sqlite3.IntegrityError as e:
            print(f"  ⚠️  Erro: {e}")
    
    # Criar empréstimos devolvidos
    used_books = set(book_ids[:10])
    available_books = [bid for bid in book_ids if bid not in used_books]
    
    for i in range(min(15, len(user_ids), len(available_books))):
        user_id = user_ids[i % len(user_ids)]
        book_id = available_books[i % len(available_books)]
        
        days_ago = random.randint(30, 180)
        data_emprestimo = datetime.now() - timedelta(days=days_ago)
        data_devolucao_prevista = data_emprestimo + timedelta(days=15)
        data_devolucao_real = data_devolucao_prevista + timedelta(days=random.randint(-5, 10))
        
        try:
            cursor.execute("""
                INSERT INTO emprestimos (id_utilizador, id_livro, data_emprestimo, data_devolucao_prevista, status, data_devolucao_real)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, book_id, data_emprestimo, data_devolucao_prevista, 'devolvido', data_devolucao_real))
            
            print(f"  ✅ Empréstimo devolvido: Utilizador {user_id}, Livro {book_id}")
        except sqlite3.IntegrityError as e:
            print(f"  ⚠️  Erro: {e}")
    
    conn.commit()
    print("✅ Empréstimos processados!")

def show_statistics(conn):
    """Mostrar estatísticas"""
    print("\n📊 Estatísticas:")
    print("=" * 40)
    
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM utilizadores")
    total_users = cursor.fetchone()[0]
    print(f"👥 Utilizadores: {total_users}")
    
    cursor.execute("SELECT COUNT(*) FROM livros")
    total_books = cursor.fetchone()[0]
    print(f"📚 Livros: {total_books}")
    
    cursor.execute("SELECT COUNT(*) FROM emprestimos")
    total_loans = cursor.fetchone()[0]
    print(f"📋 Empréstimos: {total_loans}")
    
    print("\n✅ Base de dados populada!")
    print("\n🔐 Credenciais:")
    print("Admin: ana.silva@biblioteca.pt / admin123")
    print("Professor: maria.pereira@escola.pt / prof123")
    print("Aluno: pedro.goncalves@aluno.pt / aluno123")

def main():
    """Função principal"""
    print("🚀 População da Base de Dados WebLibrary")
    print("=" * 50)
    
    try:
        conn = create_connection()
        print(f"✅ Conectado: {get_db_path()}")
        
        insert_users(conn)
        insert_books(conn)
        insert_loans(conn)
        show_statistics(conn)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main() 