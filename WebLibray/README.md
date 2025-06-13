# 📚 Sistema de Gestão de Biblioteca

Um sistema moderno e completo para gestão de bibliotecas desenvolvido com Flask, SQLite e tecnologias web modernas.

## ✨ Características

### 🔐 Autenticação e Autorização
- Sistema de login/registo seguro
- Três tipos de utilizadores: **Admin**, **Professor**, **Aluno**
- Gestão de sessões e permissões
- Hashing seguro de passwords

### 📖 Gestão de Livros
- Catálogo completo com pesquisa avançada
- Upload de capas de livros
- Categorização e filtros
- Detalhes completos (título, autor, ISBN, descrição)
- Sistema de status (disponível/emprestado)

### 🤝 Sistema de Empréstimos
- Empréstimo e devolução de livros
- Limite de 3 livros por utilizador
- Renovação de empréstimos (7 dias)
- Controlo de atrasos automático
- Histórico completo de empréstimos

### 👥 Gestão de Utilizadores (Admin)
- Criar, editar e eliminar utilizadores
- Reset de passwords
- Pesquisa e filtros
- Gestão de tipos de utilizador

### 📊 Dashboard e Relatórios
- Estatísticas em tempo real
- Gráficos e métricas
- Relatórios mensais
- Top livros mais emprestados
- Utilizadores mais ativos

### 🎨 Interface Moderna
- Design responsivo (mobile-first)
- Paleta de cores profissional
- Animações e transições suaves
- Componentes interativos
- Sistema de notificações

## 🚀 Tecnologias Utilizadas

### Backend
- **Python 3.8+**
- **Flask** - Framework web
- **SQLite** - Base de dados
- **Werkzeug** - Utilities e segurança
- **Jinja2** - Template engine

### Frontend
- **HTML5** - Estrutura
- **CSS3** - Estilização (Flexbox/Grid)
- **JavaScript** - Interatividade
- **Font Awesome** - Ícones
- **Design Responsivo**

### Paleta de Cores
- 🔵 **Primária**: `#3E8EDE` (Azul institucional)
- ⚪ **Secundária**: `#F4F4F9` (Cinza claro)
- ⚫ **Texto**: `#2D2D2D` (Cinza escuro)
- 🟡 **Destaque**: `#E3B505` (Amarelo suave)
- 🔷 **Ações**: `#51C4D3` (Turquesa)

## 📁 Estrutura do Projeto

```
biblioteca_app/
│
├── static/
│   ├── css/
│   │   └── style.css          # Estilos principais
│   ├── js/
│   │   └── main.js            # JavaScript principal
│   └── images/
│       └── covers/            # Capas dos livros
│
├── templates/
│   ├── base.html              # Template base
│   ├── login.html             # Página de login
│   ├── register.html          # Página de registo
│   ├── dashboard_admin.html   # Dashboard admin
│   ├── dashboard_aluno.html   # Dashboard aluno
│   ├── dashboard_professor.html # Dashboard professor
│   ├── livros/                # Templates de livros
│   ├── emprestimos/           # Templates de empréstimos
│   ├── utilizadores/          # Templates de utilizadores
│   └── admin/                 # Templates admin
│
├── routes/
│   ├── livros.py              # Rotas dos livros
│   ├── emprestimos.py         # Rotas dos empréstimos
│   ├── admin.py               # Rotas admin
│   └── profile.py             # Rotas do perfil
│
├── db/
│   └── biblioteca.db          # Base de dados SQLite
│
├── app.py                     # Aplicação principal
├── requirements.txt           # Dependências Python
└── README.md                  # Este arquivo
```

## 🔧 Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- pip (gestor de pacotes Python)

### Passos de Instalação

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd biblioteca_app
```

2. **Crie um ambiente virtual** (recomendado)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Execute a aplicação**
```bash
python app.py
```

5. **Aceda à aplicação**
Abra o browser em: `http://localhost:5000`

## 👤 Credenciais de Demonstração

### Administrador
- **Email**: `admin@biblioteca.com`
- **Password**: `admin123`

### Utilizadores de Teste
Pode criar novos utilizadores através da página de registo ou o admin pode criar através do painel administrativo.

## 💾 Base de Dados

O sistema utiliza SQLite com as seguintes tabelas:

### `utilizadores`
- id, nome, email, password, tipo, data_criacao

### `livros`
- id, titulo, autor, categoria, isbn, capa_url, status, data_adicao, descricao

### `emprestimos`
- id, id_utilizador, id_livro, data_emprestimo, data_devolucao_prevista, data_devolucao_real, status

## 🔒 Funcionalidades de Segurança

- Hashing de passwords com Werkzeug
- Validação de formulários
- Sanitização de uploads
- Controlo de sessões
- Verificação de permissões
- Proteção contra SQL injection

## 📱 Responsividade

O sistema é totalmente responsivo e funciona em:
- 💻 **Desktop** (1200px+)
- 📱 **Tablet** (768px - 1199px)
- 📱 **Mobile** (< 768px)

## 🎯 Funcionalidades Principais

### Para Alunos/Professores:
- ✅ Ver catálogo de livros
- ✅ Pesquisar livros por título/autor/categoria
- ✅ Solicitar empréstimos
- ✅ Ver histórico de empréstimos
- ✅ Renovar empréstimos
- ✅ Devolver livros
- ✅ Gerir perfil pessoal

### Para Administradores:
- ✅ Todas as funcionalidades dos utilizadores
- ✅ Gerir livros (criar, editar, eliminar)
- ✅ Gerir utilizadores
- ✅ Ver todos os empréstimos
- ✅ Gerar relatórios
- ✅ Ver estatísticas do sistema
- ✅ Upload de capas de livros

## 🔄 Fluxo de Empréstimos

1. **Utilizador** pesquisa e seleciona livro
2. **Sistema** verifica disponibilidade e limites
3. **Empréstimo** é criado com prazo de 15 dias
4. **Status** do livro muda para "emprestado"
5. **Utilizador** pode renovar por mais 7 dias
6. **Sistema** marca como atrasado após prazo
7. **Devolução** liberta o livro para outros

## 🎨 Personalização

### Cores
Edite as variáveis CSS no início de `static/css/style.css`:
```css
:root {
    --primary-color: #3E8EDE;
    --secondary-color: #F4F4F9;
    --accent-1: #2D2D2D;
    --accent-2: #E3B505;
    --accent-3: #51C4D3;
}
```

### Logo/Branding
- Substitua o ícone no header em `templates/base.html`
- Atualize o título da aplicação
- Modifique as informações de contacto no footer

## 🐛 Resolução de Problemas

### Erro de Base de Dados
```bash
# Elimine o ficheiro de base de dados e reinicie
rm db/biblioteca.db
python app.py
```

### Problemas de Dependências
```bash
# Reinstale as dependências
pip install --upgrade -r requirements.txt
```

### Erro de Permissions
```bash
# No Linux/Mac, certifique-se das permissões
chmod +x app.py
```

## 🔮 Funcionalidades Futuras

- [ ] Sistema de reservas
- [ ] Notificações por email
- [ ] API REST
- [ ] Integração com sistemas externos
- [ ] Sistema de multas
- [ ] Relatórios avançados
- [ ] Backup automático
- [ ] Sistema de favoritos
- [ ] Recomendações personalizadas

## 📞 Suporte

Para questões ou problemas:
- 📧 Email: biblioteca@escola.pt
- 📱 Telefone: +351 123 456 789

## 📜 Licença

Este projeto é desenvolvido para fins educacionais. 

---

**Desenvolvido com ❤️ para modernizar a gestão de bibliotecas**
