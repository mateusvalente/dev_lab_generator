# Dev Lab Generator

Gerador de laboratórios Docker para ensino de CRUD com banco, backend e frontend selecionáveis.

O projeto cria um ambiente completo em `output/<slug-do-projeto>` com:

- banco de dados `mysql` ou `oracle`
- backend opcional `php`, `java`, `node`, `python` ou `none`
- frontend opcional `vue-spa`, `vue-mpa`, `angular-spa`, `next-spa`, `next-mpa` ou `none`
- `docker-compose.yml`, `.env`, `.env.example` e `README.md` próprios do projeto gerado
- serviço `lab_info` com um resumo rápido do ambiente em execução

## Credenciais padrão

As senhas do gerador são fixas, sem valores dinâmicos:

- MySQL root: `admin`
- MySQL app user `labuser`: `admin`
- Oracle SYS/SYSTEM: `admin`
- Oracle app user `LABUSER`: `admin`

## URLS padrão

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- MySQL: `http://localhost:3306`
- Oracle: `http://localhost:1521`
- Admin do banco: `http://localhost:8080`

## Como usar

```bash
python generate_lab.py
python generate_lab.py --help
```

O fluxo interativo pede:

1. descrição do projeto
2. banco de dados
3. backend
4. frontend

Depois disso, o laboratório é gerado em `output/<slug-da-descricao>`.

## Estrutura gerada

Um projeto gerado normalmente contém:

- `docker-compose.yml`
- `.env`
- `.env.example`
- `README.md`
- `database/init/01-schema.sql`
- `backend/`
- `frontend/`

## Como subir um laboratório

Entre na pasta do projeto gerado e suba o ambiente:

```bash
cd output/<slug-do-projeto>
docker compose up --build
```

Se você já executou esse mesmo laboratório antes e alterou banco, senha ou estrutura inicial, prefira recriar também os volumes:

```bash
docker compose down -v --remove-orphans
docker compose up --build
```

Isso é especialmente importante para Oracle e MySQL, porque os volumes persistem credenciais e dados de execuções anteriores.

## Como usar o `lab_info`

Cada projeto gerado inclui um serviço chamado `lab_info`. Ele mostra no log:

- nome do projeto
- stack escolhida
- portas
- credenciais
- URL do admin do banco
- caminhos principais para editar backend, frontend e banco

Para ver as informações com o ambiente já em execução:

```bash
cd output/<slug-do-projeto>
docker compose logs lab_info
```

Para ver só as últimas linhas:

```bash
docker compose logs lab_info --tail 50
```

Se quiser acompanhar em tempo real:

```bash
docker compose logs -f lab_info
```

## Observações sobre Oracle

O scaffold Oracle usa:

- `gvenzl/oracle-free:23-slim-faststart` para o banco
- `container-registry.oracle.com/database/ords:latest` para ORDS / Database Actions

Em alguns ambientes, a imagem do ORDS pode exigir aceite prévio no Oracle Container Registry.

## Observações sobre regeneração

Ao regenerar o mesmo projeto, o gerador atualiza os arquivos do scaffold. Porém, se o banco já tiver sido inicializado antes, o volume Docker continua existindo até você remover com `docker compose down -v --remove-orphans`.

Na prática:

- regenerar atualiza código, compose, `.env` e README
- remover volumes reinicializa o banco com os valores atuais do projeto
