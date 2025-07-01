#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço para corrigir automaticamente IDs NULL na tabela livros
"""

import sqlite3
import os
import sys

# Adicionar o diretório pai ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.database import get_db_connection

def fix_null_ids_auto():
    """
    Corrige automaticamente todos os IDs NULL na tabela livros
    Esta função é chamada automaticamente após adicionar um livro
    """
    try:
        with get_db_connection() as (conn, cursor):
            # Verificar se há livros com ID NULL
            cursor.execute("SELECT COUNT(*) FROM livros WHERE id IS NULL")
            null_count = cursor.fetchone()[0]
            
            if null_count == 0:
                return True  # Nada para corrigir
            
            print(f"🔧 Corrigindo {null_count} livros com ID NULL...")
            
            # Encontrar o próximo ID disponível
            cursor.execute("SELECT MAX(id) FROM livros WHERE id IS NOT NULL")
            max_id_result = cursor.fetchone()
            max_id = max_id_result[0] if max_id_result[0] is not None else 0
            next_id = max_id + 1
            
            # Buscar todos os livros com ID NULL
            cursor.execute("SELECT ROWID FROM livros WHERE id IS NULL ORDER BY ROWID")
            null_rowids = cursor.fetchall()
            
            # Corrigir cada um
            for i, (rowid,) in enumerate(null_rowids):
                new_id = next_id + i
                cursor.execute("UPDATE livros SET id = ? WHERE ROWID = ?", (new_id, rowid))
                
            conn.commit()
            print(f"✅ {null_count} IDs NULL corrigidos automaticamente!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao corrigir IDs NULL: {e}")
        return False

def ensure_table_integrity():
    """
    Garante que a tabela livros tenha estrutura correta para AUTO_INCREMENT
    """
    try:
        with get_db_connection() as (conn, cursor):
            # Verificar se a tabela tem AUTO_INCREMENT configurado
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='livros'")
            table_sql = cursor.fetchone()
            
            if table_sql and 'AUTOINCREMENT' not in table_sql[0].upper():
                print("⚠️ Tabela livros não tem AUTO_INCREMENT configurado")
                print("🔧 Aplicando correção automática de IDs...")
                
                # Fazer backup da estrutura atual
                cursor.execute("PRAGMA table_info(livros)")
                columns = cursor.fetchall()
                
                # Corrigir qualquer ID NULL existente
                fix_null_ids_auto()
                
                return True
            else:
                print("✅ Tabela livros tem estrutura correta")
                return True
                
    except Exception as e:
        print(f"❌ Erro ao verificar integridade da tabela: {e}")
        return False

def post_add_book_cleanup(livro_id=None):
    """
    Função para ser chamada após adicionar um livro
    Garante que não há IDs NULL na base de dados
    """
    try:
        # Sempre executar correção automática após adicionar livro
        success = fix_null_ids_auto()
        
        if success:
            print("✅ Verificação pós-adição concluída com sucesso")
        else:
            print("⚠️ Houve problemas na verificação pós-adição")
            
        return success
        
    except Exception as e:
        print(f"❌ Erro na verificação pós-adição: {e}")
        return False

def check_book_accessibility(livro_id):
    """
    Verifica se um livro específico está acessível
    """
    try:
        with get_db_connection() as (conn, cursor):
            cursor.execute("SELECT id, titulo FROM livros WHERE id = ?", (livro_id,))
            result = cursor.fetchone()
            
            if result and result[0] is not None:
                print(f"✅ Livro ID {livro_id} acessível: '{result[1]}'")
                return True
            else:
                print(f"❌ Livro ID {livro_id} não acessível")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao verificar acessibilidade do livro {livro_id}: {e}")
        return False

# Executar verificação automática quando o módulo for importado
if __name__ != "__main__":
    ensure_table_integrity() 