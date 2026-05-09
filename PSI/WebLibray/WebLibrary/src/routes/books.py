from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from src.models.database import get_db_connection
import sqlite3
from datetime import datetime
import os
from src.services.auto_fix_service import post_add_book_cleanup, fix_null_ids_auto

books_bp = Blueprint("books", __name__)

@books_bp.route("/catalog")
def catalog():
    """Exibir catálogo de livros com filtros e pesquisa"""
    # Parâmetros de pesquisa e filtros com valores seguros
    search = request.args.get("search", "").strip()
    categoria = request.args.get("categoria", "")
    sort_by = request.args.get("sort_by", "titulo")
    order = request.args.get("order", "asc")
    page = max(1, request.args.get("page", 1, type=int))
    per_page = min(48, max(12, request.args.get("per_page", 12, type=int)))
    
    # 🔧 VERIFICAÇÃO AUTOMÁTICA: Corrigir IDs NULL ao aceder ao catálogo
    try:
        fix_null_ids_auto()
    except Exception as e:
        print(f"⚠️ Aviso: Erro na verificação automática: {e}")
    
    try:
        
        with get_db_connection() as (conn, cursor):
            # Contar registros com filtros
            count_query = "SELECT COUNT(*) FROM livros WHERE 1=1"
            count_params = []
            
            if search:
                count_query += " AND (titulo LIKE ? OR autor LIKE ? OR isbn LIKE ?)"
                search_param = f"%{search}%"
                count_params.extend([search_param, search_param, search_param])
            
            if categoria:
                count_query += " AND categoria = ?"
                count_params.append(categoria)
            
            cursor.execute(count_query, count_params)
            total_records = cursor.fetchone()[0]
            
            # Calcular paginação - forçar valores seguros
            if total_records == 0:
                total_pages = 1
                page = 1
                offset = 0
            else:
                total_pages = max(1, (total_records + per_page - 1) // per_page)
                page = max(1, min(page, total_pages))
                offset = (page - 1) * per_page
            

            # Query principal com paginação - versão simplificada e robusta
            if total_records == 0:
                livros_data = []
            else:
                query = """SELECT id, titulo, autor, categoria, ano_publicacao, status, isbn, 
                                 editora, paginas, idioma, descricao, data_adicao, capa_url 
                          FROM livros WHERE 1=1"""
                params = []
                
                if search:
                    query += " AND (titulo LIKE ? OR autor LIKE ? OR isbn LIKE ?)"
                    search_param = f"%{search}%"
                    params.extend([search_param, search_param, search_param])
                
                if categoria:
                    query += " AND categoria = ?"
                    params.append(categoria)
                
                # Ordenação simplificada
                if sort_by == "autor":
                    query += f" ORDER BY autor {'DESC' if order == 'desc' else 'ASC'}"
                elif sort_by == "categoria":
                    query += f" ORDER BY categoria {'DESC' if order == 'desc' else 'ASC'}"
                elif sort_by == "ano_publicacao":
                    query += f" ORDER BY ano_publicacao {'DESC' if order == 'desc' else 'ASC'}"
                elif sort_by == "data_adicao":
                    query += f" ORDER BY data_adicao {'DESC' if order == 'desc' else 'ASC'}"
                else:
                    # Padrão: título
                    query += f" ORDER BY titulo {'DESC' if order == 'desc' else 'ASC'}"
                
                # Só adicionar LIMIT se tiver registros
                if offset < total_records:
                    query += " LIMIT ? OFFSET ?"
                    params.extend([per_page, offset])
                
                cursor.execute(query, params)
                livros_data = cursor.fetchall()
            
            # Converter tuplas em dicionários para o template
            livros = []
            if livros_data:
                for livro_data in livros_data:
                    try:
                        livro = {
                            "id": livro_data[0] or 0,
                            "titulo": livro_data[1] or "Sem título",
                            "autor": livro_data[2] or "Autor desconhecido",
                            "categoria": livro_data[3] or "Sem categoria",
                            "ano_publicacao": livro_data[4] or "",
                            "status": livro_data[5] or "disponivel",
                            "isbn": livro_data[6] or "",
                            "editora": livro_data[7] or "",
                            "paginas": livro_data[8] or "",
                            "idioma": livro_data[9] or "Português",
                            "descricao": livro_data[10] or "",
                            "data_adicao": livro_data[11] or "",
                            "capa_url": livro_data[12] or ""
                        }
                        livros.append(livro)
                    except Exception as e:
                        continue
            

            
            # Obter categorias para o filtro - com fallback
            try:
                cursor.execute("SELECT DISTINCT categoria FROM livros WHERE categoria IS NOT NULL ORDER BY categoria")
                categorias = [row[0] for row in cursor.fetchall() if row[0]]
                if not categorias:
                    # Fallback para categorias padrão se não houver nenhuma
                    categorias = ["Arte", "Autoajuda", "Biografia", "Ciência", "Culinária", "Direito", 
                                "Economia", "Educação", "Desporto", "Ficção", "Ficção Científica", 
                                "Filosofia", "Geografia", "História", "Infantil", "Literatura Clássica", 
                                "Línguas", "Matemática", "Medicina e Saúde", "Psicologia", "Religião", 
                                "Romance", "Tecnologia"]
            except Exception as e:
                categorias = ["Ficção", "Não-Ficção"]  # Categorias mínimas
        
        # Preparar variáveis de paginação
        has_prev = page > 1
        has_next = page < total_pages
        prev_page = page - 1 if has_prev else None
        next_page = page + 1 if has_next else None
        
        # Gerar números de página para exibir
        page_numbers = []
        if total_pages <= 7:
            page_numbers = list(range(1, total_pages + 1))
        else:
            if page <= 4:
                page_numbers = list(range(1, 6)) + ["...", total_pages]
            elif page >= total_pages - 3:
                page_numbers = [1, "..."] + list(range(total_pages - 4, total_pages + 1))
            else:
                page_numbers = [1, "..."] + list(range(page - 1, page + 2)) + ["...", total_pages]
        
        def build_url(**kwargs):
            """Função auxiliar para construir URLs de paginação"""
            args = {
                "search": search,
                "categoria": categoria,
                "sort_by": sort_by,
                "order": order,
                "per_page": per_page
            }
            args.update(kwargs)
            # Remove parâmetros vazios
            args = {k: v for k, v in args.items() if v}
            query_string = "&".join(f"{k}={v}" for k, v in args.items())
            return f"{url_for('books.catalog')}?{query_string}"
        
        return render_template("books/catalog.html", 
                             livros=livros,
                             categorias=categorias,
                             search=search,
                             categoria=categoria,
                             sort_by=sort_by,
                             order=order,
                             page=page,
                             per_page=per_page,
                             total_pages=total_pages,
                             total_records=total_records,
                             has_prev=has_prev,
                             has_next=has_next,
                             prev_page=prev_page,
                             next_page=next_page,
                             page_numbers=page_numbers,
                             build_url=build_url)
                             
    except Exception as e:
        print(f"❌ ERRO CRÍTICO no catálogo: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback para dados básicos em caso de erro
        return render_template("books/catalog.html", 
                             livros=[],
                             categorias=[],
                             search="",
                             categoria="",
                             sort_by="titulo",
                             order="asc",
                             page=1,
                             per_page=12,
                             total_pages=1,
                             total_records=0,
                             has_prev=False,
                             has_next=False,
                             prev_page=None,
                             next_page=None,
                             page_numbers=[1],
                             build_url=lambda **kwargs: url_for('books.catalog'))

@books_bp.route("/details/<int:livro_id>")
def details(livro_id):
    """Exibir detalhes de um livro específico"""
    print(f"🔍 DETAILS CHAMADA: ID {livro_id}")
    try:
        with get_db_connection() as (conn, cursor):
            # Verificar se o livro existe
            cursor.execute("SELECT COUNT(*) FROM livros WHERE id = ?", (livro_id,))
            existe = cursor.fetchone()[0]
            print(f"🔍 Livro ID {livro_id} existe: {existe > 0}")
            
            if existe == 0:
                print(f"❌ Livro ID {livro_id} NÃO ENCONTRADO!")
                flash("Livro não encontrado.", "error")
                return redirect(url_for("books.catalog"))
            
            # Buscar dados completos do livro
            cursor.execute("""
                SELECT id, titulo, autor, categoria, ano_publicacao, status, isbn, editora, 
                       paginas, idioma, descricao, data_adicao, capa_url
                FROM livros WHERE id = ?
            """, (livro_id,))
            
            livro_data = cursor.fetchone()
            
            if livro_data:
                # Conversão segura da data
                data_adicao = None
                if livro_data[11]:
                    data_raw = str(livro_data[11]).strip()
                    
                    if data_raw and data_raw != 'None':
                        try:
                            # Formato completo: 2024-01-15 14:30:25
                            data_adicao = datetime.strptime(data_raw, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            try:
                                # Apenas data: 2024-01-15
                                data_adicao = datetime.strptime(data_raw, "%Y-%m-%d")
                            except ValueError:
                                try:
                                    # Formato brasileiro: 15/01/2024
                                    data_adicao = datetime.strptime(data_raw, "%d/%m/%Y")
                                except ValueError:
                                    try:
                                        # Formato com espaços extras
                                        data_clean = ' '.join(data_raw.split())
                                        data_adicao = datetime.strptime(data_clean, "%Y-%m-%d %H:%M:%S")
                                    except ValueError:
                                        # Manter como string se nenhum formato funcionar
                                        data_adicao = data_raw
                
                # Criação segura do objeto livro
                try:
                    livro = {
                        "id": int(livro_data[0]) if livro_data[0] is not None else 0,
                        "titulo": str(livro_data[1]).strip() if livro_data[1] else "Sem título",
                        "autor": str(livro_data[2]).strip() if livro_data[2] else "Autor desconhecido",
                        "categoria": str(livro_data[3]).strip() if livro_data[3] else "Sem categoria",
                        "ano": str(livro_data[4]).strip() if livro_data[4] else "",
                        "status": str(livro_data[5]).strip() if livro_data[5] else "disponivel",
                        "isbn": str(livro_data[6]).strip() if livro_data[6] else "",
                        "editora": str(livro_data[7]).strip() if livro_data[7] else "",
                        "paginas": str(livro_data[8]).strip() if livro_data[8] else "",
                        "idioma": str(livro_data[9]).strip() if livro_data[9] else "Português",
                        "descricao": str(livro_data[10]).strip() if livro_data[10] else "",
                        "data_adicao": data_adicao,
                        "capa_url": str(livro_data[12]).strip() if livro_data[12] else "",
                        "localizacao": "Biblioteca Principal"
                    }
                    
                    # 📚 BUSCAR LIVROS RELACIONADOS (mesma categoria)
                    livros_relacionados = []
                    try:
                        cursor.execute("""
                            SELECT id, titulo, autor, categoria, ano_publicacao, status, capa_url
                            FROM livros 
                            WHERE categoria = ? AND id != ? AND id IS NOT NULL
                            ORDER BY RANDOM()
                            LIMIT 6
                        """, (livro["categoria"], livro_id))
                        
                        relacionados_data = cursor.fetchall()
                        
                        for rel_data in relacionados_data:
                            livro_relacionado = {
                                "id": rel_data[0],
                                "titulo": str(rel_data[1]).strip() if rel_data[1] else "Sem título",
                                "autor": str(rel_data[2]).strip() if rel_data[2] else "Autor desconhecido",
                                "categoria": str(rel_data[3]).strip() if rel_data[3] else "Sem categoria",
                                "ano": str(rel_data[4]).strip() if rel_data[4] else "",
                                "status": str(rel_data[5]).strip() if rel_data[5] else "disponivel",
                                "capa_url": str(rel_data[6]).strip() if rel_data[6] else ""
                            }
                            livros_relacionados.append(livro_relacionado)
                        
                        print(f"📚 Encontrados {len(livros_relacionados)} livros relacionados na categoria '{livro['categoria']}'")
                        
                    except Exception as e:
                        print(f"⚠️ Erro ao buscar livros relacionados: {e}")
                        livros_relacionados = []  # Fallback para lista vazia
                    
                    return render_template("books/details.html", livro=livro, livros_relacionados=livros_relacionados)
                    
                except Exception as e:
                    print(f"❌ ERRO ao criar objeto livro: {e}")
                    # Fallback com dados mínimos em caso de erro
                    livro = {
                        "id": livro_id,
                        "titulo": "Título não disponível",
                        "autor": "Autor não disponível",
                        "categoria": "Sem categoria",
                        "ano": "",
                        "status": "disponivel",
                        "isbn": "",
                        "editora": "",
                        "paginas": "",
                        "idioma": "Português",
                        "descricao": "",
                        "data_adicao": None,
                        "capa_url": "",
                        "localizacao": "Biblioteca Principal"
                    }
                    
                    print(f"⚠️ Usando dados de fallback para livro ID {livro_id}")
                    return render_template("books/details.html", livro=livro, livros_relacionados=[])
            else:
                print(f"❌ Query não retornou dados para ID {livro_id}")
                flash("Erro ao carregar dados do livro.", "error")
                return redirect(url_for("books.catalog"))
                
    except Exception as e:
        print(f"❌ ERRO CRÍTICO ao buscar livro {livro_id}: {e}")
        import traceback
        traceback.print_exc()
        flash("Erro interno ao carregar detalhes do livro.", "error")
        return redirect(url_for("books.catalog"))

@books_bp.route("/add", methods=["GET", "POST"])
def add_book():
    """Adicionar novo livro (apenas admins)"""

    if session.get("user_type") != "admin":
        flash("Acesso negado. Apenas administradores podem adicionar livros.", "error")
        return redirect(url_for("books.catalog"))
    
    if request.method == "POST":
        try:
            # Obter dados do formulário
            titulo = request.form.get("titulo")
            autor = request.form.get("autor")
            categoria = request.form.get("categoria")
            isbn = request.form.get("isbn")
            ano = request.form.get("ano")
            editora = request.form.get("editora")
            paginas = request.form.get("paginas")
            idioma = request.form.get("idioma", "Português")
            descricao = request.form.get("descricao")
            status = request.form.get("status", "disponivel")
            
            # Validação básica
            if not titulo or not autor or not categoria:
                flash("Título, autor e categoria são obrigatórios.", "error")
                return render_template("books/add_book.html")
            
            # Processar upload de capa (se fornecida)
            capa_url = None
            if 'capa' in request.files:
                capa_file = request.files['capa']
                if capa_file and capa_file.filename != '':
                    from werkzeug.utils import secure_filename
                    import uuid
                    
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                    filename = secure_filename(capa_file.filename)
                    file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                    
                    if file_extension in allowed_extensions:
                        unique_filename = f"{uuid.uuid4()}.{file_extension}"
                        from flask import current_app
                        upload_folder = current_app.config['UPLOAD_FOLDER']
                        os.makedirs(upload_folder, exist_ok=True)
                        
                        file_path = os.path.join(upload_folder, unique_filename)
                        capa_file.save(file_path)
                        capa_url = f"/static/images/covers/{unique_filename}"
                    else:
                        flash("Formato de arquivo não suportado. Use PNG, JPG, JPEG ou GIF.", "error")
                        return render_template("books/add_book.html")
            
            with get_db_connection() as (conn, cursor):
                data_adicao_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                cursor.execute("""
                    INSERT INTO livros (titulo, autor, categoria, isbn, ano_publicacao, editora, 
                                      paginas, idioma, descricao, status, capa_url, data_adicao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (titulo, autor, categoria, isbn, ano, editora, paginas, 
                      idioma, descricao, status, capa_url, data_adicao_atual))
                
                livro_id = cursor.lastrowid
                conn.commit()
                print(f"✅ Livro '{titulo}' adicionado com ID: {livro_id}")
                
            # 🔧 CORREÇÃO AUTOMÁTICA: Garantir que não há IDs NULL após adicionar livro
            try:
                print("🔧 Executando correção automática de IDs NULL...")
                post_add_book_cleanup(livro_id)
                print("✅ Correção automática concluída com sucesso!")
            except Exception as fix_error:
                print(f"⚠️ Aviso: Erro na correção automática: {fix_error}")
                # Não falhar a adição por causa disso, apenas avisar

            flash("Livro adicionado com sucesso!", "success")
            return redirect(url_for("books.catalog"))
            
        except Exception as e:
            print(f"Erro ao adicionar livro: {e}")
            flash("Erro ao adicionar livro. Tente novamente.", "error")
    
    return render_template("books/add_book.html")

@books_bp.route("/edit/<int:livro_id>", methods=["GET", "POST"])
def edit_book(livro_id):
    """Editar livro existente (apenas admins)"""
    if session.get("user_type") != "admin":
        flash("Acesso negado. Apenas administradores podem editar livros.", "error")
        return redirect(url_for("books.details", livro_id=livro_id))
    
    if request.method == "POST":
        try:
            # Obter dados do formulário
            titulo = request.form.get("titulo")
            autor = request.form.get("autor")
            categoria = request.form.get("categoria")
            isbn = request.form.get("isbn")
            ano = request.form.get("ano")
            editora = request.form.get("editora")
            paginas = request.form.get("paginas")
            idioma = request.form.get("idioma", "Português")
            descricao = request.form.get("descricao")
            status = request.form.get("status", "disponivel")
            
            # Validação básica
            if not titulo or not autor or not categoria:
                flash("Título, autor e categoria são obrigatórios.", "error")
                return redirect(url_for("books.edit_book", livro_id=livro_id))
            
            # Processar upload de capa (se fornecida)
            capa_url = None
            if 'capa' in request.files:
                capa_file = request.files['capa']
                if capa_file and capa_file.filename != '':
                    from werkzeug.utils import secure_filename
                    import uuid
                    
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                    filename = secure_filename(capa_file.filename)
                    file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                    
                    if file_extension in allowed_extensions:
                        unique_filename = f"{uuid.uuid4()}.{file_extension}"
                        from flask import current_app
                        upload_folder = current_app.config['UPLOAD_FOLDER']
                        os.makedirs(upload_folder, exist_ok=True)
                        
                        file_path = os.path.join(upload_folder, unique_filename)
                        capa_file.save(file_path)
                        capa_url = f"/static/images/covers/{unique_filename}"
                    else:
                        flash("Formato de arquivo não suportado. Use PNG, JPG, JPEG ou GIF.", "error")
                        return redirect(url_for("books.edit_book", livro_id=livro_id))
            
            with get_db_connection() as (conn, cursor):
                if capa_url:
                    cursor.execute("""
                        UPDATE livros 
                        SET titulo=?, autor=?, categoria=?, isbn=?, ano_publicacao=?, editora=?, 
                            paginas=?, idioma=?, descricao=?, status=?, capa_url=?
                        WHERE id=?
                    """, (titulo, autor, categoria, isbn, ano, editora, paginas, 
                          idioma, descricao, status, capa_url, livro_id))
                else:
                    cursor.execute("""
                        UPDATE livros 
                        SET titulo=?, autor=?, categoria=?, isbn=?, ano_publicacao=?, editora=?, 
                            paginas=?, idioma=?, descricao=?, status=?
                        WHERE id=?
                    """, (titulo, autor, categoria, isbn, ano, editora, paginas, 
                          idioma, descricao, status, livro_id))
                
                conn.commit()
                
            flash("Livro atualizado com sucesso!", "success")
            return redirect(url_for("books.details", livro_id=livro_id))
            
        except Exception as e:
            print(f"Erro ao atualizar livro: {e}")
            flash("Erro ao atualizar livro. Tente novamente.", "error")
    
    # GET - mostrar formulário de edição
    try:
        with get_db_connection() as (conn, cursor):
            cursor.execute("""
                SELECT id, titulo, autor, categoria, ano_publicacao, status, isbn, editora, 
                       paginas, idioma, descricao, data_adicao, capa_url
                FROM livros WHERE id = ?
            """, (livro_id,))
            
            livro_data = cursor.fetchone()
            
            if livro_data:
                # Conversão segura da data
                data_adicao = None
                if livro_data[11]:
                    try:
                        # Tentar formato completo primeiro
                        data_adicao = datetime.strptime(livro_data[11], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        try:
                            # Tentar formato só de data
                            data_adicao = datetime.strptime(livro_data[11], "%Y-%m-%d")
                        except ValueError:
                            try:
                                # Tentar outros formatos comuns
                                data_adicao = datetime.strptime(livro_data[11], "%d/%m/%Y")
                            except ValueError:
                                # Se nada funcionar, manter como string
                                data_adicao = livro_data[11]
                
                livro = {
                    "id": livro_data[0] or 0,
                    "titulo": livro_data[1] or "Sem título",
                    "autor": livro_data[2] or "Autor desconhecido",
                    "categoria": livro_data[3] or "Sem categoria",
                    "ano": livro_data[4] or "",
                    "status": livro_data[5] or "disponivel",
                    "isbn": livro_data[6] or "",
                    "editora": livro_data[7] or "",
                    "paginas": livro_data[8] or "",
                    "idioma": livro_data[9] or "Português",
                    "descricao": livro_data[10] or "",
                    "data_adicao": data_adicao,
                    "capa_url": livro_data[12] or ""
                }
                
                return render_template("books/edit_book.html", livro=livro)
            else:
                flash("Livro não encontrado.", "error")
                return redirect(url_for("books.catalog"))
                
    except Exception as e:
        print(f"Erro ao carregar livro para edição: {e}")
        flash("Erro ao carregar livro para edição.", "error")
        return redirect(url_for("books.catalog"))

@books_bp.route("/delete/<int:livro_id>", methods=["POST"])
def delete_book(livro_id):
    """Excluir livro (apenas admins)"""
    if session.get("user_type") != "admin":
        flash("Acesso negado. Apenas administradores podem excluir livros.", "error")
        return redirect(url_for("books.details", livro_id=livro_id))
    
    try:
        with get_db_connection() as (conn, cursor):
            cursor.execute("DELETE FROM livros WHERE id = ?", (livro_id,))
            conn.commit()
        flash("Livro excluído com sucesso!", "success")
    except Exception as e:
        print(f"Erro ao excluir livro: {e}")
        flash("Erro ao excluir livro. Tente novamente.", "error")
    
    return redirect(url_for("books.catalog"))

@books_bp.route("/search")
def search_books():
    """Página de resultados de pesquisa (redireciona para o catálogo com o termo de pesquisa)"""
    search_term = request.args.get("query", "").strip()
    return redirect(url_for("books.catalog", search=search_term))


