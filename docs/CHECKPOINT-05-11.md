# Checkpoint 1 · 05/11

Primeira etapa do projeto da disciplina GAC116, conforme a seção 5.1 do enunciado. O checkpoint vale 20 pontos; o trabalho completo vale 45 pontos.

| Critério | Peso | Evidência |
| --- | --- | --- |
| Modelagem completa | 20% | `MODELAGEM.md`, oito entidades, relação N:N, migrações e constraints |
| Ambiente administrativo | 20% | `/admin/`, autenticação, CRUD e grupos com permissões |
| Templates administrativos | 10% | Jazzmin instalado antes de `django.contrib.admin`, tema Flatly com modos claro/escuro e identidade Fólio |
| Diferentes filtros | 10% | Filtros de categoria/editora/ano e filtro próprio de situação de empréstimo |
| Organização do repositório | 10% | Separação entre frontend, backend e documentação; migrações e lockfile; fluxo de branches descrito em `GITHUB.md` |
| Complexidade | 30% | Dois apps, oito entidades, transações, integridade, permissões, Preact integrado |

## Roteiro de apresentação (6–8 minutos)

1. Apresentar o problema: biblioteca precisa controlar obras, unidades físicas, leitores e circulação.
2. Mostrar o DER em `MODELAGEM.md`. Explicar a diferença Livro/Exemplar, a autoria N:N e a preservação do histórico.
3. Entrar no Django Admin com o usuário criado localmente. Mostrar Jazzmin e as oito entidades.
4. Abrir Livros e combinar categoria, editora e ano. Buscar por autor. Abrir um livro e mostrar autores e exemplares embutidos.
5. Abrir Empréstimos e alternar o filtro de situação entre atraso, aberto e devolvido. Mostrar os filtros de datas e categoria.
6. Acessar o painel Preact com o mesmo usuário (login próprio na porta 5173). Pesquisar no acervo, cadastrar um livro e registrar um empréstimo.
7. Devolver o exemplar, mostrando que a disponibilidade muda. Tentar excluir um livro com histórico para evidenciar a proteção.
8. Mostrar os grupos Bibliotecários e Consulta; um usuário de Consulta com `is_staff` pode consultar, mas não gravar.
9. Abrir repositório público, README, migrações, branches e contribuições de cada integrante.

O acesso autenticado utiliza o banco SQLite. O modo de demonstração permite explorar a interface com dados temporários em memória.

## Versionamento e entrega

O enunciado estabelece repositório público no GitHub, branches `main`, `develop` e `feature`, participação de todos os integrantes como colaboradores e pelo menos dois commits por integrante durante o desenvolvimento. O prazo de envio do link no Campus Virtual é **05/11 às 12h00**.

## Segunda etapa

O checkpoint de 19/11 abrange a conclusão da aplicação, incluindo cadastro público e área de usuário final.
