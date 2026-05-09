#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para executar a aplicação WebLibrary
"""

import os
import sys

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(__file__))

# Verificar se estamos no diretório correto
current_dir = os.getcwd()
expected_file = os.path.join(current_dir, 'src', 'main.py')

if not os.path.exists(expected_file):
    print("❌ Erro: Não foi possível encontrar src/main.py")
    print(f"📁 Diretório atual: {current_dir}")
    print("💡 Certifique-se de que está no diretório 'weblibrary'")
    print("\n🔧 Para corrigir:")
    print("   cd home/ubuntu/weblibrary_project/weblibrary_completo_v2/weblibrary")
    print("   python run_app.py")
    sys.exit(1)

print("✅ Diretório correto encontrado!")
print(f"📁 A executar a partir de: {current_dir}")

# Verificar se a base de dados existe
db_path = os.path.join('src', 'database', 'weblibrary.db')
if os.path.exists(db_path):
    print(f"✅ Base de dados encontrada: {db_path}")
else:
    print(f"⚠️ Base de dados não encontrada: {db_path}")

# Verificar utilizadores admin
try:
    import sqlite3
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nome, email, tipo FROM utilizadores WHERE tipo = 'admin'")
    admins = cursor.fetchall()
    
    print(f"\n👥 Administradores encontrados: {len(admins)}")
    for admin in admins:
        print(f"   ID: {admin[0]} | {admin[1]} | {admin[2]}")
    
    conn.close()
    
    if len(admins) == 0:
        print("\n⚠️ AVISO: Nenhum administrador encontrado!")
        print("💡 Use as credenciais padrão para fazer login como admin:")
        print("   Email: admin@weblibrary.com")
        print("   Password: admin123")
        
except Exception as e:
    print(f"❌ Erro ao verificar utilizadores: {e}")

print("\n🚀 A iniciar a aplicação...")
print("📌 Para aceder: http://localhost:5000")
print("🔑 Credenciais de admin padrão:")
print("   Email: admin@weblibrary.com")
print("   Password: admin123")
print("\n⭐ Funcionalidades disponíveis para admins:")
print("   - Adicionar livros (botão no catálogo)")
print("   - Editar livros existentes") 
print("   - Gerir utilizadores")
print("   - Ver relatórios")

print("\n" + "="*50)

# Importar e executar a aplicação
try:
    from src.main import app
    app.run(host='0.0.0.0', port=5000, debug=True)
except Exception as e:
    print(f"❌ Erro ao iniciar a aplicação: {e}")
    import traceback
    traceback.print_exc() 