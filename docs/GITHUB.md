# Organização do repositório

O desenvolvimento utiliza três branches principais:

- `main`: versão estável.
- `develop`: integração das funcionalidades.
- `feature`: desenvolvimento das funcionalidades da etapa.

Branches adicionais podem seguir o padrão `feature/nome-da-tarefa`.

## Configuração inicial

```powershell
git init -b main
git add .
git commit -m "feat: implementa checkpoint com Preact e Django"
git branch develop
git branch feature
```

O `.gitignore` exclui dependências, ambientes virtuais, bancos SQLite, configurações locais e caches. As migrações e `package-lock.json` fazem parte do versionamento. A autoria dos commits é configurada com `git config user.name` e `git config user.email`.

## Sincronização com o GitHub

Após criar um repositório público vazio, configure a URL do remoto:

```powershell
git remote add origin https://github.com/mattheus-jordany/folio-gest-o-de-biblioteca-programacao-web.git
git push -u origin main
git push -u origin develop
git push -u origin feature
```

## Colaboração

Os integrantes são adicionados em Settings → Collaborators. As alterações partem de `feature` ou de uma branch específica da tarefa, são integradas em `develop` e, após validação, em `main`. Cada integrante participa com sua conta e realiza pelo menos dois commits durante o desenvolvimento, conforme os requisitos da disciplina.

Antes da integração, executar o build do frontend, a verificação do Django e os testes descritos no README.
