# Fólio · Gestão de biblioteca

Projeto da disciplina GAC116 — Programação Web.

Sistema de gestão de bibliotecas com catálogo de livros, controle de exemplares físicos, cadastro de leitores, empréstimos e reservas. A interface utiliza **Preact** e se comunica com uma API **Django**. A administração dos dados utiliza o Django Admin com tema Jazzmin.

## Integrantes

| Integrante | Matrícula |
| --- | --- |
| Mattheus Jordany Vicente Rodrigues | 202410414 |
| Marina Barbosa Valim | 202410197 |

## Tecnologias

- Preact 10, Vite 6 e Bootstrap 5; CSS responsivo com temas claro e escuro.
- Django 5.2 LTS, Django Admin com Jazzmin e SQLite relacional.
- Autenticação por sessão, proteção CSRF e permissões nativas do Django.
- Dois apps de domínio: `catalog` e `circulation`.

## Instalação (Windows / PowerShell)

Pré-requisitos: Node.js 22.15+ e Python 3.10+ disponíveis no PATH; Git para versionamento. O código não depende de CDN de JavaScript. Fontes do Google são opcionais e têm fallback local.

```powershell
git clone https://github.com/mattheus-jordany/folio-gest-o-de-biblioteca-programacao-web.git
cd folio-gest-o-de-biblioteca-programacao-web
npm ci
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\.venv\Scripts\python.exe backend/manage.py migrate
.\.venv\Scripts\python.exe backend/manage.py seed_demo
```

O último comando pede uma senha de pelo menos dez caracteres e cria o usuário `admin`, além de oito livros, 24 exemplares, seis leitores, cinco empréstimos e uma reserva. A senha não é gravada em código. Se o administrador já existir, o comando o preserva. Se não quiser dados demonstrativos, utilize `createsuperuser` no lugar de `seed_demo`.

No Windows, o comando `py` pode ser utilizado no lugar de `python`, conforme a instalação do Python.

## Execução

Abra dois terminais na pasta do projeto:

```powershell
# Terminal 1 — Django
.\.venv\Scripts\python.exe backend/manage.py runserver 127.0.0.1:8000
```

```powershell
# Terminal 2 — Preact
npm run dev
```

- Interface: http://127.0.0.1:5173
- Administração completa com Jazzmin: http://127.0.0.1:8000/admin/
- Entre com as credenciais criadas por `seed_demo` ou `createsuperuser`.
- **Explorar demonstração** permite navegar sem o backend, com dados fictícios em memória, descartados ao sair ou recarregar. O acesso autenticado utiliza os dados persistidos no SQLite.

## Funcionalidades

- Painel Preact com indicadores calculados a partir do banco.
- Consulta, cadastro, edição e exclusão de livros; inclusão de exemplares no cadastro.
- Cadastro de leitores, empréstimos e reservas; registro de devoluções.
- Busca por título, autor, ISBN, nome e matrícula; filtros por categoria e situação.
- Django Admin com CRUD completo das oito entidades, Jazzmin, pesquisa, filtros, autocompletar, seleção múltipla de autores e exemplares embutidos nos livros.
- Filtro administrativo próprio: empréstimos em aberto, em atraso ou devolvidos.
- Perfis: superusuário (gestão completa), Bibliotecários (consulta, inclusão e edição) e Consulta (somente leitura). Para os dois últimos, criar usuário com `is_staff` e atribuir o grupo pelo admin.
- Integridade no banco: ISBN, tombo, e-mail e matrícula únicos; apenas um empréstimo ativo por exemplar; apenas uma reserva em espera por livro/leitor; datas consistentes; histórico protegido contra exclusão.
- Layout responsivo, alternância de tema e formulários com foco e teclado.

A interface Preact oferece as operações mais frequentes. A manutenção completa de autores, categorias, editoras, exemplares, leitores e reservas é feita no Django Admin.

O escopo da primeira etapa concentra-se na modelagem, administração e circulação do acervo. Cadastro público e área individual do leitor fazem parte da segunda etapa.

## Verificação

```powershell
npm run build
.\.venv\Scripts\python.exe backend/manage.py check
.\.venv\Scripts\python.exe backend/manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe backend/manage.py test circulation
```

As migrações iniciais fazem parte do código-fonte. O banco SQLite, os ambientes virtuais e os arquivos de configuração local são ignorados pelo Git.

## Estrutura

```text
src/                    Interface Preact e demonstração em memória
backend/config/         Configuração Django, rotas e tema Jazzmin
backend/catalog/        Autor, categoria, editora, livro e exemplar
backend/circulation/    Leitor, empréstimo, reserva, API, testes e seed
docs/MODELAGEM.md        DER, campos, cardinalidades e regras
docs/CHECKPOINT-05-11.md Roteiro e requisitos da entrega
docs/GITHUB.md          Organização e publicação do repositório
```

## Documentação

- [Modelagem do banco de dados](docs/MODELAGEM.md)
- [Escopo e roteiro do checkpoint 1](docs/CHECKPOINT-05-11.md)
- [Fluxo de versionamento](docs/GITHUB.md)

## Configuração fora do desenvolvimento

O backend lê `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` e `DJANGO_ALLOWED_HOSTS` das variáveis de ambiente do sistema. O arquivo `.env.example` documenta os nomes; arquivos `.env` não são carregados automaticamente. Exemplo no PowerShell:

```powershell
$env:DJANGO_SECRET_KEY = 'sua-chave-local'
$env:DJANGO_DEBUG = '1'
$env:DJANGO_ALLOWED_HOSTS = 'localhost,127.0.0.1'
```

A configuração padrão é destinada ao desenvolvimento local. Para hospedar, configurar uma chave secreta própria, `DJANGO_DEBUG=0`, hosts permitidos, HTTPS, origem CSRF, arquivos estáticos e servidor de aplicação. O Vite faz proxy de `/api`, `/admin` e `/static` durante o desenvolvimento; o link do admin utiliza a porta 8000. O build Preact gera `dist/`, e sua hospedagem exige encaminhar a API para o Django.

## Referências técnicas

- [Preact: guia](https://preactjs.com/guide/v10/getting-started/)
- [Vite: configuração](https://vite.dev/config/)
- [Django: ambiente administrativo e filtros](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/)
- [Jazzmin: configuração](https://django-jazzmin.readthedocs.io/configuration/)
