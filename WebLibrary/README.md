# 📚 WebLibrary - Sistema de Gestão de Biblioteca

## 🏫 Sobre o Projeto

**WebLibrary** é um sistema completo de gestão de biblioteca desenvolvido especificamente para a **BE Florbela Espanca** da ESMCargaleiro. O sistema oferece uma solução moderna e intuitiva para a gestão de livros, empréstimos, utilizadores e documentos de estudo.

### 🎯 Objetivos
- Digitalizar e modernizar a gestão da biblioteca escolar
- Facilitar o acesso aos recursos bibliográficos para alunos e professores
- Automatizar processos de empréstimo e devolução
- Implementar sistema de multas por atraso
- Centralizar documentos de estudo por disciplina e ano escolar

## ✨ Funcionalidades Principais

### 👤 Sistema de Utilizadores
- **Registo e autenticação** segura de utilizadores
- **Três tipos de conta**: Admin, Professor, Aluno
- **Perfis personalizáveis** com foto, biografia e preferências
- **Gestão de dados pessoais** e configurações de notificação

### 📖 Gestão de Livros
- **Catálogo digital** com pesquisa avançada e filtros
- **Informações detalhadas** de livros (título, autor, categoria, ISBN, descrição)
- **Sistema de capas** com upload e visualização
- **Livros relacionados** por categoria
- **Gestão de disponibilidade** em tempo real

### 🔄 Sistema de Empréstimos
- **Requisição online** de livros
- **Gestão automática** de prazos de devolução
- **Sistema de renovação** (uma vez por empréstimo)
- **Histórico completo** de empréstimos por utilizador
- **Notificações automáticas** de prazo e atrasos

### 💰 Sistema de Multas
- **Cálculo automático** de multas por atraso (€0.50/dia)
- **Notificações por email** em múltiplos estágios (5, 15, 30+ dias)
- **Gestão de pagamentos** e histórico de multas

### 📑 Documentos de Estudo
- **Upload de documentos** organizados por disciplina e ano
- **Sistema de tags** para categorização
- **Download controlado** com estatísticas

### 📊 Dashboard e Relatórios
- **Dashboard administrativo** com estatísticas em tempo real
- **Gráficos interativos** de utilização mensal
- **Atividade recente** do sistema
- **Relatórios detalhados** com filtros personalizáveis

## 🔧 Tecnologias Utilizadas

### Backend
- **Python 3.11+** - Linguagem principal
- **Flask** - Framework web modular e flexível
- **SQLite** - Base de dados embebida
- **Werkzeug** - Segurança e hashing de passwords

### Frontend
- **HTML5** - Estrutura semântica
- **CSS3** - Estilização moderna e responsiva
- **JavaScript ES6+** - Interatividade e dinamismo
- **Bootstrap 5** - Framework CSS responsivo
- **Font Awesome** - Iconografia

## 📁 Estrutura do Projeto

```
weblibrary/
├── run_app.py                    # Ponto de entrada da aplicação
├── populate_database.py          # População inicial da BD
│
├── src/                          # Código fonte principal
│   ├── main.py                   # Configuração da aplicação Flask
│   │
│   ├── models/                   # Modelos de dados
│   │   ├── database.py           # Gestão da base de dados
│   │   └── user.py               # Modelo de utilizador
│   │
│   ├── routes/                   # Rotas da aplicação
│   │   ├── main.py               # Rotas principais e dashboard
│   │   ├── auth.py               # Autenticação e registo
│   │   ├── books.py              # Gestão de livros
│   │   ├── loans.py              # Sistema de empréstimos
│   │   ├── admin.py              # Funcionalidades administrativas
│   │   ├── users.py              # Gestão de utilizadores
│   │   ├── documentos.py         # Sistema de documentos
│   │   └── multas.py             # Sistema de multas
│   │
│   ├── services/                 # Serviços auxiliares
│   │   ├── auto_fix_service.py   # Correção automática de dados
│   │   └── multas_service.py     # Processamento de multas
│   │
│   ├── templates/                # Templates HTML
│   │   ├── layouts/              # Layouts base
│   │   ├── auth/                 # Templates de autenticação
│   │   ├── books/                # Templates de livros
│   │   ├── loans/                # Templates de empréstimos
│   │   ├── admin/                # Templates administrativos
│   │   ├── users/                # Templates de utilizador
│   │   ├── documentos/           # Templates de documentos
│   │   ├── dashboard/            # Templates de dashboard
│   │   └── components/           # Componentes reutilizáveis
│   │
│   ├── static/                   # Recursos estáticos
│   │   ├── css/                  # Estilos CSS
│   │   ├── js/                   # Scripts JavaScript
│   │   ├── images/               # Imagens e ícones
│   │   └── uploads/              # Ficheiros enviados
│   │
│   └── database/                 # Base de dados
│       └── weblibrary.db         # Ficheiro SQLite
│
└── logs/                         # Logs do sistema
    └── emails/                   # Templates de email
```

## 🚀 Instalação e Configuração

### Pré-requisitos
- **Python 3.11 ou superior**
- **pip** (gestor de pacotes Python)
- **Web browser** moderno

### Passo 1: Instalar Dependências
```bash
pip install flask werkzeug jinja2
```

### Passo 2: Executar a Aplicação
```bash
# Windows
python run_app.py

# Linux/macOS
python3 run_app.py
```

### Passo 3: Aceder ao Sistema
- **URL**: http://127.0.0.1:5000
- **Dashboard Admin**: http://127.0.0.1:5000/dashboard

## 🔐 Credenciais de Acesso

### Conta Administrador
- **Email**: admin@weblibrary.com
- **Password**: admin123
- **Permissões**: Acesso total ao sistema

## 📋 Base de Dados

### Estrutura das Tabelas

#### 👥 utilizadores
- **id** (Primary Key)
- **nome** - Nome completo
- **email** - Email único
- **password** - Password encriptada
- **tipo** - admin/professor/aluno
- **data_criacao** - Data de registo

#### 📚 livros
- **id** (Primary Key)
- **titulo, autor, categoria** - Informações básicas
- **isbn** - Código único do livro
- **capa_url** - Caminho para imagem da capa
- **status** - disponivel/emprestado
- **data_adicao** - Data de adição ao catálogo

#### 🔄 emprestimos
- **id** (Primary Key)
- **id_utilizador, id_livro** - Chaves estrangeiras
- **data_emprestimo** - Data do empréstimo
- **data_devolucao_prevista** - Data limite para devolução
- **data_devolucao_real** - Data efetiva de devolução
- **status** - ativo/devolvido/atrasado
- **renovado** - Se foi renovado (0/1)

#### 💰 multas
- **id** (Primary Key)
- **id_emprestimo, id_utilizador** - Referências
- **valor_total** - Valor da multa (€0.50/dia)
- **dias_atraso** - Dias de atraso
- **status** - pendente/paga/cancelada

#### 📑 documentos_estudo
- **id** (Primary Key)
- **titulo, descricao** - Informações do documento
- **ano_escolaridade, disciplina** - Organização académica
- **ficheiro, tipo_ficheiro** - Dados do arquivo
- **autor_id** - Professor que fez upload

## 🎨 Interface do Utilizador

### Design e UX
- **Design responsivo** que funciona em todos os dispositivos
- **Esquema de cores** institucional da escola
- **Navegação intuitiva** com breadcrumbs e menus claros
- **Feedback visual** para todas as ações do utilizador

### Componentes Visuais
- **Cards informativos** para estatísticas
- **Tabelas interativas** com paginação e ordenação
- **Formulários validados** com feedback em tempo real
- **Gráficos dinâmicos** para visualização de dados

## 📱 Funcionalidades Especiais

### Sistema de Notificações
- **Emails automáticos** para lembretes de devolução
- **Alertas de multa** em múltiplos estágios
- **Notificações no dashboard** para ações importantes

### Relatórios e Estatísticas
- **Dashboard em tempo real** com dados atualizados
- **Gráfico de requisições mensais** baseado em dados reais
- **Atividade recente** do sistema
- **Relatórios personalizáveis** com filtros de data

### Sistema de Pesquisa
- **Pesquisa global** em livros, utilizadores e documentos
- **Filtros avançados** por categoria, status, ano, etc.
- **Resultados paginados** para performance

## 🐛 Troubleshooting

### Problemas Comuns

#### Erro: "No such column"
```bash
# Regenerar a base de dados
python populate_database.py
```

#### Erro: "ModuleNotFoundError"
```bash
# Instalar dependências em falta
pip install flask werkzeug jinja2
```

#### Problemas de Performance
- Verificar se há muitos registos na base de dados
- Limpar logs antigos da pasta `logs/`
- Reiniciar a aplicação periodicamente

## 🔄 Manutenção

### Backups
```bash
# Backup da base de dados
cp src/database/weblibrary.db backup_$(date +%Y%m%d).db
```

### Limpeza Periódica
- **Logs antigos** (mensalmente)
- **Ficheiros temporários** (semanalmente)
- **Multas pagas antigas** (anualmente)

## 🎓 Para Utilizadores

### Alunos
1. **Registar conta** com email escolar
2. **Pesquisar livros** no catálogo
3. **Requisitar empréstimos** online
4. **Acompanhar prazos** no dashboard pessoal
5. **Descarregar documentos** de estudo

### Professores
- Todas as funcionalidades de aluno
- **Upload de documentos** de estudo
- **Gestão de materiais** da disciplina

### Administradores
- **Gestão completa** de utilizadores e livros
- **Configuração** do sistema de multas
- **Geração de relatórios** detalhados
- **Monitorização** da atividade do sistema

## 📞 Suporte e Contacto

### BE Florbela Espanca - ESMCargaleiro
- **📧 Email Biblioteca**: biblioteca@esmcargaleiro.pt
- **📞 Telefone**: 212 269 790
- **🌐 Website**: www.esmcargaleiro.pt

### Horários de Funcionamento
- **Presencial**: Segunda a Sexta, 9h-17h
- **Suporte Online**: Manhã (11h-12h), Tarde (15h-16h)
- **Email**: Resposta em 48h (dias úteis)

## 📄 Status do Sistema

**Características do Sistema:**
- ✅ Sistema completo e funcional
- ✅ Dados reais da base de dados
- ✅ Interface moderna e responsiva
- ✅ Funcionalidades avançadas implementadas
- ✅ Sistema de segurança robusto
- ✅ Pronto para uso em produção

---

**Desenvolvido com ❤️ para a educação**

*Última atualização: dezembro 2024* 