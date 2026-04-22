import re
import sys
import shutil
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).parent
TEMPLATES = BASE_DIR / 'templates'
OUTPUT_DIR = BASE_DIR / 'output'

BACKENDS = {
    '0': ('none', 'Nenhum backend'),
    '1': ('php', 'PHP'),
    '2': ('java', 'Java / Spring Boot'),
    '3': ('node', 'Node.js / Express'),
    '4': ('python', 'Python / Flask'),
}

FRONTENDS = {
    '0': ('none', 'Nenhum frontend'),
    '1': ('vue-spa', 'Vue SPA'),
    '2': ('vue-mpa', 'Vue MPA'),
    '3': ('angular-spa', 'Angular SPA'),
    '4': ('next-spa', 'Next SPA'),
    '5': ('next-mpa', 'Next MPA'),
}

DATABASES = {
    '1': ('mysql', 'MySQL + phpMyAdmin'),
    '2': ('oracle', 'Oracle Database Free + SQL Developer Web / Database Actions (ORDS)'),
}

HELP_TEXT = '''Dev Lab Generator

Uso:
  python generate_lab.py
  python generate_lab.py --help

O programa gera um laboratório Docker para ensino de CRUD com:
- banco de dados selecionável (MySQL ou Oracle)
- backend opcional (PHP, Java, Node, Python ou nenhum)
- frontend opcional (Vue SPA/MPA, Angular SPA, Next SPA/MPA ou nenhum)
- README do projeto gerado
- resumo final com portas, usuários e senhas

Observações:
- A pasta gerada fica em output/<slug-da-descricao>
- A descrição é obrigatória e vira a base do nome da pasta
- As portas são fixas e apenas informadas no resumo final
- O suporte Oracle usa um scaffold de ORDS / Database Actions no compose
'''


def banner():
    print(r'''
╔════════════════════════════════════════════════════════════════════════════╗
║                         DEV LAB GENERATOR                                ║
║            Laboratório Docker de CRUD para ensino de frameworks          ║
╚════════════════════════════════════════════════════════════════════════════╝
''')


def section(title: str):
    print(f"\n┌─ {title} " + "─" * max(1, 68 - len(title)))


def prompt(text: str) -> str:
    return input(f"➜ {text}: ").strip()


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text or 'lab-projeto'


def build_default_context(
    description: str,
    slug: str,
    db_key: str,
    db_label: str,
    backend_key: str,
    backend_label: str,
    frontend_key: str,
    frontend_label: str,
    backend_port: int,
    frontend_port: int,
    db_port: int,
    db_admin_port: int,
) -> dict:
    context = {
        'PROJECT_DESCRIPTION': description,
        'PROJECT_SLUG': slug,
        'DB_KEY': db_key,
        'DB_LABEL': db_label,
        'BACKEND_KEY': backend_key,
        'BACKEND_LABEL': backend_label,
        'FRONTEND_KEY': frontend_key,
        'FRONTEND_LABEL': frontend_label,
        'BACKEND_PORT': backend_port,
        'FRONTEND_PORT': frontend_port,
        'DB_PORT': db_port,
        'DB_ADMIN_PORT': db_admin_port,
        'DB_INTERNAL_PORT': 3306 if db_key == 'mysql' else 1521,
        'MYSQL_ROOT_PASSWORD': 'admin',
        'MYSQL_DATABASE': 'labdb',
        'MYSQL_USER': 'labuser',
        'MYSQL_PASSWORD': 'admin',
        'ORACLE_PASSWORD': 'admin',
        'ORACLE_APP_USER': 'LABUSER',
        'ORACLE_APP_PASSWORD': 'admin',
        'ORACLE_ORDS_IMAGE': 'container-registry.oracle.com/database/ords:latest',
        'API_BASE_URL': f"http://localhost:{backend_port}/api" if backend_key != 'none' else '',
    }
    context['DB_DATABASE'] = context['MYSQL_DATABASE'] if db_key == 'mysql' else 'FREEPDB1'
    context['DB_USERNAME'] = context['MYSQL_USER'] if db_key == 'mysql' else context['ORACLE_APP_USER']
    context['DB_APP_PASSWORD'] = context['MYSQL_PASSWORD'] if db_key == 'mysql' else context['ORACLE_APP_PASSWORD']
    return context


def ask_description() -> tuple[str, str]:
    while True:
        desc = prompt('Descrição do projeto (obrigatória)')
        if desc:
            return desc, slugify(desc)
        print('  ! Informe uma descrição válida.')


def choose(title, options):
    section(title)
    for key, (_, label) in options.items():
        print(f'  [{key}] {label}')
    while True:
        value = prompt('Escolha')
        if value in options:
            return options[value][0], options[value][1]
        print('  ! Opção inválida.')


def ask_yes_no(label: str, default: bool = True) -> bool:
    suffix = '[S/n]' if default else '[s/N]'
    raw = prompt(f'{label} {suffix}').lower()
    if not raw:
        return default
    return raw in {'s', 'sim', 'y', 'yes'}


def copy_tree(src: Path, dst: Path):
    if src.exists():
        shutil.copytree(src, dst, dirs_exist_ok=True)


def render_template(path: Path, context: dict):
    text = path.read_text(encoding='utf-8')
    for k, v in context.items():
        text = text.replace(f'{{{{{k}}}}}', str(v))
    path.write_text(text, encoding='utf-8')


def render_all(base: Path, context: dict):
    for p in base.rglob('*'):
        if p.is_file():
            render_template(p, context)


def mysql_services(context: dict) -> str:
    return f'''  db:
    image: mysql:8.4
    container_name: {context['PROJECT_SLUG']}-db
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${{MYSQL_ROOT_PASSWORD}}
      MYSQL_DATABASE: ${{MYSQL_DATABASE}}
      MYSQL_USER: ${{MYSQL_USER}}
      MYSQL_PASSWORD: ${{MYSQL_PASSWORD}}
    ports:
      - "{context['DB_PORT']}:3306"
    volumes:
      - db_data:/var/lib/mysql
      - ./database/init:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "mysqladmin ping -h localhost -uroot -p${{MYSQL_ROOT_PASSWORD}}"]
      interval: 10s
      timeout: 5s
      retries: 20
    networks:
      default:
        aliases:
          - db

  db_admin:
    image: phpmyadmin:5
    container_name: {context['PROJECT_SLUG']}-phpmyadmin
    restart: unless-stopped
    environment:
      PMA_HOST: db
      PMA_PORT: 3306
      PMA_USER: root
      PMA_PASSWORD: ${{MYSQL_ROOT_PASSWORD}}
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "{context['DB_ADMIN_PORT']}:80"'''


def oracle_services(context: dict) -> str:
    return f'''  db:
    image: gvenzl/oracle-free:23-slim-faststart
    container_name: {context['PROJECT_SLUG']}-oracle
    restart: unless-stopped
    environment:
      ORACLE_PASSWORD: ${{ORACLE_PASSWORD}}
      APP_USER: ${{ORACLE_APP_USER}}
      APP_USER_PASSWORD: ${{ORACLE_APP_PASSWORD}}
    ports:
      - "{context['DB_PORT']}:1521"
    volumes:
      - db_data:/opt/oracle/oradata
      - ./database/init:/container-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "healthcheck.sh"]
      interval: 30s
      timeout: 10s
      start_period: 15m
      retries: 20
    networks:
      default:
        aliases:
          - db

  db_admin:
    image: ${{ORACLE_ORDS_IMAGE}}
    container_name: {context['PROJECT_SLUG']}-ords
    restart: unless-stopped
    environment:
      DBHOST: db
      DBPORT: 1521
      DBSERVICENAME: FREEPDB1
      ORACLE_PWD: ${{ORACLE_PASSWORD}}
    volumes:
      - ords_config:/etc/ords/config
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "curl --noproxy localhost -f http://localhost:8080/ords/ || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 30
      start_period: 5m
    ports:
      - "{context['DB_ADMIN_PORT']}:8080"'''


def backend_service(context: dict) -> str:
    if context['BACKEND_KEY'] == 'none':
        return ''
    extra_volumes = []
    if context['BACKEND_KEY'] == 'node':
        extra_volumes.append('      - backend_node_modules:/app/node_modules')
    elif context['BACKEND_KEY'] == 'java':
        extra_volumes.append('      - backend_maven_cache:/root/.m2')
        extra_volumes.append('      - backend_target:/app/target')
    volumes_block = '\n'.join(['    volumes:', '      - ./backend:/app', *extra_volumes])
    health_path = '/health' if context['BACKEND_KEY'] == 'php' else '/api/health'
    return f'''  backend:
    build:
      context: ./backend
    container_name: {context['PROJECT_SLUG']}-backend
    restart: unless-stopped
    environment:
      APP_DESCRIPTION: "{context['PROJECT_DESCRIPTION']}"
      DB_CLIENT: {context['DB_KEY']}
      DB_HOST: db
      DB_PORT: {context['DB_INTERNAL_PORT']}
      DB_NAME: {context['DB_DATABASE']}
      DB_USER: {context['DB_USERNAME']}
      DB_PASSWORD: {context['DB_APP_PASSWORD']}
      DB_SCHEMA: {context['DB_USERNAME']}
      PORT: {context['BACKEND_PORT']}
    depends_on:
      db:
        condition: service_healthy
{volumes_block}
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://127.0.0.1:{context['BACKEND_PORT']}{health_path} >/dev/null || exit 1"]
      interval: 20s
      timeout: 10s
      retries: 15
      start_period: 45s
    ports:
      - "{context['BACKEND_PORT']}:{context['BACKEND_PORT']}"'''


def frontend_service(context: dict) -> str:
    if context['FRONTEND_KEY'] == 'none':
        return ''
    extra_volumes = ['      - frontend_node_modules:/app/node_modules']
    if context['FRONTEND_KEY'].startswith('next-'):
        extra_volumes.append('      - frontend_next_cache:/app/.next')
    volumes_block = '\n'.join(['    volumes:', '      - ./frontend:/app', *extra_volumes])
    depends_block = (
        '    depends_on:\n'
        '      backend:\n'
        '        condition: service_healthy'
        if context['BACKEND_KEY'] != 'none'
        else '    depends_on:\n'
             '      db:\n'
             '        condition: service_healthy'
    )
    frontend_health_lines = [
        f'curl -fsS http://127.0.0.1:{context["FRONTEND_PORT"]}/ >/dev/null',
    ]
    if context['BACKEND_KEY'] != 'none':
        backend_health_path = '/health' if context['BACKEND_KEY'] == 'php' else '/api/health'
        frontend_health_lines.append(
            f'curl -fsS http://backend:{context["BACKEND_PORT"]}{backend_health_path} >/dev/null'
        )
    frontend_health = ' && \\\n          '.join(frontend_health_lines)
    return f'''  frontend:
    build:
      context: ./frontend
    container_name: {context['PROJECT_SLUG']}-frontend
    restart: unless-stopped
    environment:
      API_BASE_URL: {context['API_BASE_URL']}
      PORT: {context['FRONTEND_PORT']}
{volumes_block}
{depends_block}
    healthcheck:
      test:
        - CMD-SHELL
        - |
          {frontend_health}
      interval: 20s
      timeout: 10s
      retries: 20
      start_period: 60s
    ports:
      - "{context['FRONTEND_PORT']}:{context['FRONTEND_PORT']}"'''


def lab_info_service(context: dict) -> str:
    depends_lines = ['    depends_on:']
    if context['DB_KEY'] == 'mysql':
        depends_lines.extend([
            '      db:',
            '        condition: service_healthy',
            '      db_admin:',
            '        condition: service_started',
        ])
    else:
        depends_lines.extend([
            '      db:',
            '        condition: service_healthy',
            '      db_admin:',
            '        condition: service_healthy',
        ])
    if context['BACKEND_KEY'] != 'none':
        depends_lines.extend([
            '      backend:',
            '        condition: service_healthy',
        ])
    if context['FRONTEND_KEY'] != 'none':
        depends_lines.extend([
            '      frontend:',
            '        condition: service_healthy',
        ])
    depends_block = '\n'.join(depends_lines)
    edit_lines = [
        "Banco: ./database/init/01-schema.sql",
        "Infra Docker: ./docker-compose.yml e ./.env",
    ]
    backend_paths = {
        'php': './backend/public/index.php',
        'java': './backend/src/main/java/lab e ./backend/src/main/resources/application.properties',
        'node': './backend/src/server.js',
        'python': './backend/app.py',
    }
    frontend_paths = {
        'vue-spa': './frontend/src',
        'vue-mpa': './frontend/src e arquivos HTML na raiz de ./frontend',
        'angular-spa': './frontend/src/main.ts e ./frontend/server.mjs',
        'next-spa': './frontend/pages e ./frontend/lib',
        'next-mpa': './frontend/pages e ./frontend/lib',
    }
    if context['BACKEND_KEY'] != 'none':
        edit_lines.append(f"Backend ({context['BACKEND_LABEL']}): {backend_paths[context['BACKEND_KEY']]}")
    if context['FRONTEND_KEY'] != 'none':
        edit_lines.append(f"Frontend ({context['FRONTEND_LABEL']}): {frontend_paths[context['FRONTEND_KEY']]}")
    access_lines = []
    if context['DB_KEY'] == 'mysql':
        access_lines.extend([
            f"MySQL root: root / {context['MYSQL_ROOT_PASSWORD']}",
            f"MySQL app: {context['MYSQL_USER']} / {context['MYSQL_PASSWORD']}",
            f"phpMyAdmin: http://localhost:{context['DB_ADMIN_PORT']}/",
        ])
    else:
        access_lines.extend([
            f"Oracle SYS/SYSTEM password: {context['ORACLE_PASSWORD']}",
            f"Oracle app user: {context['ORACLE_APP_USER']} / {context['ORACLE_APP_PASSWORD']}",
            "Oracle service: FREEPDB1",
            f"ORDS URL: http://localhost:{context['DB_ADMIN_PORT']}/ords/",
            "ORDS config no container: /etc/ords/config",
        ])
    message_lines = [
        '=== DEV LAB STACK ===',
        f"Projeto: {context['PROJECT_SLUG']}",
        f"Banco: {context['DB_LABEL']} -> localhost:{context['DB_PORT']}",
        f"Admin DB: localhost:{context['DB_ADMIN_PORT']}",
        f"Backend: {context['BACKEND_LABEL']}" + (f" -> localhost:{context['BACKEND_PORT']}" if context['BACKEND_KEY'] != 'none' else ''),
        f"Frontend: {context['FRONTEND_LABEL']}" + (f" -> localhost:{context['FRONTEND_PORT']}" if context['FRONTEND_KEY'] != 'none' else ''),
        '=== ACESSOS ===',
        *access_lines,
        '=== ONDE ALTERAR ===',
        *edit_lines,
    ]
    printf_args = '\n'.join([f'        "{line}" \\' for line in message_lines[:-1]] + [f'        "{message_lines[-1]}"'])
    return f'''  lab_info:
    image: busybox:1.36
    container_name: {context['PROJECT_SLUG']}-info
{depends_block}
    command:
      - sh
      - -c
      - |
        printf '%s\\n' \\
{printf_args}
        sleep infinity
    restart: "no"'''


def build_compose(context: dict) -> str:
    parts = ['services:', lab_info_service(context), '', mysql_services(context) if context['DB_KEY'] == 'mysql' else oracle_services(context)]
    b = backend_service(context)
    f = frontend_service(context)
    if b:
        parts.extend(['', b])
    if f:
        parts.extend(['', f])
    volumes = '\nvolumes:\n  db_data:\n'
    if context['BACKEND_KEY'] == 'node':
        volumes += '  backend_node_modules:\n'
    elif context['BACKEND_KEY'] == 'java':
        volumes += '  backend_maven_cache:\n'
        volumes += '  backend_target:\n'
    if context['DB_KEY'] == 'oracle':
        volumes += '  ords_config:\n'
    if f:
        volumes += '  frontend_node_modules:\n'
    if context['FRONTEND_KEY'].startswith('next-'):
        volumes += '  frontend_next_cache:\n'
    parts.append(volumes)
    return '\n'.join(parts)


def build_env(context: dict) -> str:
    rows = [
        f"PROJECT_DESCRIPTION={context['PROJECT_DESCRIPTION']}",
        f"DB_CLIENT={context['DB_KEY']}",
        f"BACKEND_PORT={context['BACKEND_PORT']}",
        f"FRONTEND_PORT={context['FRONTEND_PORT']}",
        f"DB_PORT={context['DB_PORT']}",
        f"DB_ADMIN_PORT={context['DB_ADMIN_PORT']}",
    ]
    if context['DB_KEY'] == 'mysql':
        rows += [
            f"MYSQL_ROOT_PASSWORD={context['MYSQL_ROOT_PASSWORD']}",
            f"MYSQL_DATABASE={context['MYSQL_DATABASE']}",
            f"MYSQL_USER={context['MYSQL_USER']}",
            f"MYSQL_PASSWORD={context['MYSQL_PASSWORD']}",
        ]
    else:
        rows += [
            f"ORACLE_PASSWORD={context['ORACLE_PASSWORD']}",
            f"ORACLE_APP_USER={context['ORACLE_APP_USER']}",
            f"ORACLE_APP_PASSWORD={context['ORACLE_APP_PASSWORD']}",
            f"ORACLE_ORDS_IMAGE={context['ORACLE_ORDS_IMAGE']}",
        ]
    return '\n'.join(rows) + '\n'


def read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        values[key.strip()] = value.strip()
    return values


def preserve_existing_credentials(context: dict, existing_env: dict[str, str]) -> dict:
    if not existing_env:
        return context
    if existing_env.get('DB_CLIENT') != context['DB_KEY']:
        return context

    preserved = dict(context)
    if context['DB_KEY'] == 'mysql':
        for key in ('MYSQL_DATABASE', 'MYSQL_USER'):
            if existing_env.get(key):
                preserved[key] = existing_env[key]
    else:
        for key in ('ORACLE_APP_USER', 'ORACLE_ORDS_IMAGE'):
            if existing_env.get(key):
                preserved[key] = existing_env[key]

    preserved['DB_DATABASE'] = preserved['MYSQL_DATABASE'] if preserved['DB_KEY'] == 'mysql' else 'FREEPDB1'
    preserved['DB_USERNAME'] = preserved['MYSQL_USER'] if preserved['DB_KEY'] == 'mysql' else preserved['ORACLE_APP_USER']
    preserved['DB_APP_PASSWORD'] = preserved['MYSQL_PASSWORD'] if preserved['DB_KEY'] == 'mysql' else preserved['ORACLE_APP_PASSWORD']
    return preserved


def build_schema(context: dict) -> str:
    if context['DB_KEY'] == 'mysql':
        return '''CREATE TABLE IF NOT EXISTS categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  description VARCHAR(255) NULL
);

CREATE TABLE IF NOT EXISTS products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  category_id INT NOT NULL,
  name VARCHAR(120) NOT NULL,
  price DECIMAL(10,2) NOT NULL DEFAULT 0,
  stock INT NOT NULL DEFAULT 0,
  CONSTRAINT fk_products_category
    FOREIGN KEY (category_id) REFERENCES categories(id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);

INSERT INTO categories (name, description) VALUES
('Eletrônicos', 'Produtos eletrônicos em geral'),
('Livros', 'Livros físicos e digitais');

INSERT INTO products (category_id, name, price, stock) VALUES
(1, 'Mouse USB', 59.90, 10),
(1, 'Teclado Mecânico', 249.90, 5),
(2, 'Algoritmos em Prática', 89.90, 20);
'''
    return '''WHENEVER SQLERROR EXIT SQL.SQLCODE;

ALTER SESSION SET CONTAINER = FREEPDB1;
ALTER SESSION SET CURRENT_SCHEMA = LABUSER;

CREATE TABLE categories (
  id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  name VARCHAR2(120) NOT NULL,
  description VARCHAR2(255)
);

CREATE TABLE products (
  id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  category_id NUMBER NOT NULL,
  name VARCHAR2(120) NOT NULL,
  price NUMBER(10,2) DEFAULT 0 NOT NULL,
  stock NUMBER DEFAULT 0 NOT NULL,
  CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories(id)
);

INSERT INTO categories (name, description) VALUES ('Eletrônicos', 'Produtos eletrônicos em geral');
INSERT INTO categories (name, description) VALUES ('Livros', 'Livros físicos e digitais');

INSERT INTO products (category_id, name, price, stock) VALUES (1, 'Mouse USB', 59.90, 10);
INSERT INTO products (category_id, name, price, stock) VALUES (1, 'Teclado Mecânico', 249.90, 5);
INSERT INTO products (category_id, name, price, stock) VALUES (2, 'Algoritmos em Prática', 89.90, 20);

COMMIT;
'''


def project_readme(context: dict) -> str:
    outputs = []
    if context['BACKEND_KEY'] != 'none':
        outputs.append(f"- Backend REST: http://localhost:{context['BACKEND_PORT']}")
    if context['FRONTEND_KEY'] != 'none':
        outputs.append(f"- Frontend: http://localhost:{context['FRONTEND_PORT']}")
    outputs.append(f"- Banco ({context['DB_KEY']}): localhost:{context['DB_PORT']}")
    outputs.append(f"- Administração do banco: http://localhost:{context['DB_ADMIN_PORT']}")

    if context['DB_KEY'] == 'mysql':
        creds = [
            f"- MySQL root: root / {context['MYSQL_ROOT_PASSWORD']}",
            f"- MySQL app: {context['MYSQL_USER']} / {context['MYSQL_PASSWORD']}",
            f"- Database: {context['MYSQL_DATABASE']}",
        ]
        note = ''
    else:
        creds = [
            f"- Oracle SYS/SYSTEM password: {context['ORACLE_PASSWORD']}",
            f"- Oracle app user: {context['ORACLE_APP_USER']} / {context['ORACLE_APP_PASSWORD']}",
            '- Service name: FREEPDB1',
        ]
        note = (
            '\n> Observação: o acesso web do Oracle depende do ORDS / Database Actions. '
            'O gerador já monta o scaffold no `docker-compose.yml`, mas a imagem pode exigir '
            'aceite prévio no Oracle Container Registry, dependendo do ambiente.\n'
        )
    backend_edit = {
        'none': '- Backend: não gerado nesta combinação',
        'php': '- Backend PHP: `backend/public/index.php`',
        'java': '- Backend Java: `backend/src/main/java/lab/` e `backend/src/main/resources/application.properties`',
        'node': '- Backend Node: `backend/src/server.js`',
        'python': '- Backend Python: `backend/app.py`',
    }
    frontend_edit = {
        'none': '- Frontend: não gerado nesta combinação',
        'vue-spa': '- Frontend Vue SPA: `frontend/src/`',
        'vue-mpa': '- Frontend Vue MPA: `frontend/src/` e arquivos `.html` na raiz de `frontend/`',
        'angular-spa': '- Frontend Angular SPA: `frontend/src/main.ts` e `frontend/server.mjs`',
        'next-spa': '- Frontend Next SPA: `frontend/pages/` e `frontend/lib/`',
        'next-mpa': '- Frontend Next MPA: `frontend/pages/` e `frontend/lib/`',
    }
    health_lines = [
        '- Banco: usa healthcheck nativo do container do banco.',
        '- Backend: só fica `healthy` se responder HTTP e conseguir consultar o banco.',
    ]
    if context['FRONTEND_KEY'] != 'none':
        if context['BACKEND_KEY'] != 'none':
            health_lines.append('- Frontend: só fica `healthy` se subir localmente e conseguir acessar o health do backend.')
        else:
            health_lines.append('- Frontend: fica `healthy` quando o servidor web sobe e responde localmente.')
    if context['DB_KEY'] == 'oracle' and context['BACKEND_KEY'] == 'php':
        health_lines.append('- Limitação atual: PHP + Oracle sobe a infra, mas a API retorna `501 Not Implemented`.')

    return f'''# {context['PROJECT_SLUG']}

## O que é este projeto

{context['PROJECT_DESCRIPTION']}

Este laboratório foi gerado pelo **Dev Lab Generator** para servir como base didática de desenvolvimento full stack com CRUD.

## Stack escolhida

- Banco: **{context['DB_LABEL']}**
- Backend: **{context['BACKEND_LABEL']}**
- Frontend: **{context['FRONTEND_LABEL']}**

## Estrutura funcional

As entidades de exemplo são:
- `categories`
- `products`

As rotas REST esperadas no backend são:
- `GET /api/categories`
- `GET /api/categories/{{id}}`
- `POST /api/categories`
- `PUT /api/categories/{{id}}`
- `DELETE /api/categories/{{id}}`
- `GET /api/products`
- `GET /api/products/{{id}}`
- `POST /api/products`
- `PUT /api/products/{{id}}`
- `DELETE /api/products/{{id}}`

## Portas e acessos

{chr(10).join(outputs)}

## Credenciais iniciais

{chr(10).join(creds)}
{note}

## Onde alterar

- Banco e dados iniciais: `database/init/01-schema.sql`
{backend_edit[context['BACKEND_KEY']]}
{frontend_edit[context['FRONTEND_KEY']]}
- Infra e portas: `docker-compose.yml` e `.env`

## Healthchecks

{chr(10).join(health_lines)}

## Como subir

```bash
docker compose up --build
```

## Arquivos importantes

- `docker-compose.yml`: orquestração principal
- `.env`: variáveis ativas do ambiente
- `.env.example`: cópia de referência das variáveis
- `database/init/01-schema.sql`: criação das tabelas e carga inicial
- `backend/`: API escolhida
- `frontend/`: interface escolhida

## Resumo de configuração

- O backend recebe `DB_CLIENT` para adaptar a conexão entre MySQL e Oracle.
- Os drivers do banco correspondente são instalados no backend gerado.
- Quando o backend for `nenhum`, o frontend é gerado desacoplado da API.
- Quando o frontend for `nenhum`, o laboratório fica orientado a backend e banco.
'''


def print_summary(context: dict, destination: Path):
    section('Resumo final')
    print(f"  Projeto:        {context['PROJECT_SLUG']}")
    print(f"  Descrição:      {context['PROJECT_DESCRIPTION']}")
    print(f"  Banco:          {context['DB_LABEL']}")
    print(f"  Backend:        {context['BACKEND_LABEL']}")
    print(f"  Frontend:       {context['FRONTEND_LABEL']}")
    print(f"  Pasta gerada:   {destination.resolve()}")

    section('Acesso aos servidores do ambiente')
    if context['BACKEND_KEY'] != 'none':
        print(f"  Backend API:         http://localhost:{context['BACKEND_PORT']}")
    if context['FRONTEND_KEY'] != 'none':
        print(f"  Frontend:            http://localhost:{context['FRONTEND_PORT']}")
    print('  Banco de dados:')
    print('    Host:              localhost')
    print(f"    Porta:             {context['DB_PORT']}")
    print(f"    Tipo:              {context['DB_KEY']}")
    if context['DB_KEY'] == 'mysql':
        print(f"    Database:          {context['MYSQL_DATABASE']}")
        print(f"  phpMyAdmin:          http://localhost:{context['DB_ADMIN_PORT']}")
    else:
        print('    Service name:      FREEPDB1')
        print(f"  SQL Developer Web:   http://localhost:{context['DB_ADMIN_PORT']}")

    print('\n  Credenciais:')
    if context['DB_KEY'] == 'mysql':
        print(f"    - root / {context['MYSQL_ROOT_PASSWORD']}")
        print(f"    - {context['MYSQL_USER']} / {context['MYSQL_PASSWORD']}")
        print(f"    - database: {context['MYSQL_DATABASE']}")
    else:
        print(f"    - SYS/SYSTEM password: {context['ORACLE_PASSWORD']}")
        print(f"    - {context['ORACLE_APP_USER']} / {context['ORACLE_APP_PASSWORD']}")
        print('    - service: FREEPDB1')

    print('\n  Configurado:')
    print('    - README do projeto gerado')
    print('    - docker-compose dinâmico')
    print('    - schema inicial das duas tabelas')
    print('    - variáveis de conexão por banco')
    print('    - arquivo .env gerado automaticamente')
    print('    - drivers do banco no backend')

    print('\n  Próximos passos:')
    print(f'    cd {destination}')
    print('    docker compose up --build')


HELP_TEXT = '''Dev Lab Generator

Uso:
  python generate_lab.py
  python generate_lab.py --help

O programa gera um laboratório Docker para ensino de CRUD com:
- banco de dados selecionável (MySQL ou Oracle)
- backend opcional (PHP, Java, Node, Python ou nenhum)
- frontend opcional (Vue SPA/MPA, Angular SPA, Next SPA/MPA ou nenhum)
- README do projeto gerado
- resumo final com portas, usuários e senhas

Observações:
- A pasta gerada fica em output/<slug-da-descricao>
- A descrição é obrigatória e vira a base do nome da pasta
- As portas são fixas e apenas informadas no resumo final
- O suporte Oracle usa um scaffold de ORDS / Database Actions no compose
'''


def banner():
    print(r'''
╔════════════════════════════════════════════════════════════════════════════╗
║                         DEV LAB GENERATOR                                ║
║            Laboratório Docker de CRUD para ensino de frameworks          ║
╚════════════════════════════════════════════════════════════════════════════╝
''')


def section(title: str):
    print(f"\n┌─ {title} " + "─" * max(1, 68 - len(title)))


def prompt(text: str) -> str:
    return input(f"➜ {text}: ").strip()


def ask_description() -> tuple[str, str]:
    while True:
        desc = prompt('Descrição do projeto (obrigatória)')
        if desc:
            return desc, slugify(desc)
        print('  ! Informe uma descrição válida.')


def choose(title, options):
    section(title)
    for key, (_, label) in options.items():
        print(f'  [{key}] {label}')
    while True:
        value = prompt('Escolha')
        if value in options:
            return options[value][0], options[value][1]
        print('  ! Opção inválida.')


def mysql_services(context: dict) -> str:
    return f'''  db:
    image: mysql:8.4
    container_name: {context['PROJECT_SLUG']}-db
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${{MYSQL_ROOT_PASSWORD}}
      MYSQL_DATABASE: ${{MYSQL_DATABASE}}
      MYSQL_USER: ${{MYSQL_USER}}
      MYSQL_PASSWORD: ${{MYSQL_PASSWORD}}
    command:
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci
    ports:
      - "{context['DB_PORT']}:3306"
    volumes:
      - db_data:/var/lib/mysql
      - ./database/init:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "mysqladmin ping -h localhost -uroot -p${{MYSQL_ROOT_PASSWORD}}"]
      interval: 10s
      timeout: 5s
      retries: 20
    networks:
      default:
        aliases:
          - db

  db_admin:
    image: phpmyadmin:5
    container_name: {context['PROJECT_SLUG']}-phpmyadmin
    restart: unless-stopped
    environment:
      PMA_HOST: db
      PMA_PORT: 3306
      PMA_USER: root
      PMA_PASSWORD: ${{MYSQL_ROOT_PASSWORD}}
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "{context['DB_ADMIN_PORT']}:80"'''


def build_schema(context: dict) -> str:
    if context['DB_KEY'] == 'mysql':
        database_name = context.get('MYSQL_DATABASE', 'labdb')
        return f'''SET NAMES utf8mb4;
ALTER DATABASE {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  description VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  category_id INT NOT NULL,
  name VARCHAR(120) NOT NULL,
  price DECIMAL(10,2) NOT NULL DEFAULT 0,
  stock INT NOT NULL DEFAULT 0,
  CONSTRAINT fk_products_category
    FOREIGN KEY (category_id) REFERENCES categories(id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO categories (name, description) VALUES
('Eletrônicos', 'Produtos eletrônicos em geral'),
('Livros', 'Livros físicos e digitais');

INSERT INTO products (category_id, name, price, stock) VALUES
(1, 'Mouse USB', 59.90, 10),
(1, 'Teclado Mecânico', 249.90, 5),
(2, 'Algoritmos em Prática', 89.90, 20);
'''
    return '''WHENEVER SQLERROR EXIT SQL.SQLCODE;

ALTER SESSION SET CONTAINER = FREEPDB1;

CREATE TABLE categories (
  id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  name VARCHAR2(120) NOT NULL,
  description VARCHAR2(255)
);

CREATE TABLE products (
  id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  category_id NUMBER NOT NULL,
  name VARCHAR2(120) NOT NULL,
  price NUMBER(10,2) DEFAULT 0 NOT NULL,
  stock NUMBER DEFAULT 0 NOT NULL,
  CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories(id)
);

INSERT INTO categories (name, description) VALUES ('Eletrônicos', 'Produtos eletrônicos em geral');
INSERT INTO categories (name, description) VALUES ('Livros', 'Livros físicos e digitais');

INSERT INTO products (category_id, name, price, stock) VALUES (1, 'Mouse USB', 59.90, 10);
INSERT INTO products (category_id, name, price, stock) VALUES (1, 'Teclado Mecânico', 249.90, 5);
INSERT INTO products (category_id, name, price, stock) VALUES (2, 'Algoritmos em Prática', 89.90, 20);

COMMIT;
'''


def project_readme(context: dict) -> str:
    outputs = []
    if context['BACKEND_KEY'] != 'none':
        outputs.append(f"- Backend REST: http://localhost:{context['BACKEND_PORT']}")
    if context['FRONTEND_KEY'] != 'none':
        outputs.append(f"- Frontend: http://localhost:{context['FRONTEND_PORT']}")
    outputs.append(f"- Banco ({context['DB_KEY']}): localhost:{context['DB_PORT']}")
    outputs.append(f"- Administração do banco: http://localhost:{context['DB_ADMIN_PORT']}")

    if context['DB_KEY'] == 'mysql':
        creds = [
            f"- MySQL root: root / {context['MYSQL_ROOT_PASSWORD']}",
            f"- MySQL app: {context['MYSQL_USER']} / {context['MYSQL_PASSWORD']}",
            f"- Database: {context['MYSQL_DATABASE']}",
        ]
        note = ''
    else:
        creds = [
            f"- Oracle SYS/SYSTEM password: {context['ORACLE_PASSWORD']}",
            f"- Oracle app user: {context['ORACLE_APP_USER']} / {context['ORACLE_APP_PASSWORD']}",
            '- Service name: FREEPDB1',
        ]
        note = (
            '\n> Observação: o acesso web do Oracle depende do ORDS / Database Actions. '
            'O gerador já monta o scaffold no `docker-compose.yml`, mas a imagem pode exigir '
            'aceite prévio no Oracle Container Registry, dependendo do ambiente.\n'
        )
    backend_edit = {
        'none': '- Backend: não gerado nesta combinação',
        'php': '- Backend PHP: `backend/public/index.php`',
        'java': '- Backend Java: `backend/src/main/java/lab/` e `backend/src/main/resources/application.properties`',
        'node': '- Backend Node: `backend/src/server.js`',
        'python': '- Backend Python: `backend/app.py`',
    }
    frontend_edit = {
        'none': '- Frontend: não gerado nesta combinação',
        'vue-spa': '- Frontend Vue SPA: `frontend/src/`',
        'vue-mpa': '- Frontend Vue MPA: `frontend/src/` e arquivos `.html` na raiz de `frontend/`',
        'angular-spa': '- Frontend Angular SPA: `frontend/src/main.ts` e `frontend/server.mjs`',
        'next-spa': '- Frontend Next SPA: `frontend/pages/` e `frontend/lib/`',
        'next-mpa': '- Frontend Next MPA: `frontend/pages/` e `frontend/lib/`',
    }
    health_lines = [
        '- Banco: usa healthcheck nativo do container do banco.',
        '- Backend: só fica `healthy` se responder HTTP e conseguir consultar o banco.',
    ]
    if context['FRONTEND_KEY'] != 'none':
        if context['BACKEND_KEY'] != 'none':
            health_lines.append('- Frontend: só fica `healthy` se subir localmente e conseguir acessar o health do backend.')
        else:
            health_lines.append('- Frontend: fica `healthy` quando o servidor web sobe e responde localmente.')
    if context['DB_KEY'] == 'oracle' and context['BACKEND_KEY'] == 'php':
        health_lines.append('- Limitação atual: PHP + Oracle sobe a infra, mas a API retorna `501 Not Implemented`.')

    return f'''# {context['PROJECT_SLUG']}

## O que é este projeto

{context['PROJECT_DESCRIPTION']}

Este laboratório foi gerado pelo **Dev Lab Generator** para servir como base didática de desenvolvimento full stack com CRUD.

## Stack escolhida

- Banco: **{context['DB_LABEL']}**
- Backend: **{context['BACKEND_LABEL']}**
- Frontend: **{context['FRONTEND_LABEL']}**

## Estrutura funcional

As entidades de exemplo são:
- `categories`
- `products`

As rotas REST esperadas no backend são:
- `GET /api/categories`
- `GET /api/categories/{{id}}`
- `POST /api/categories`
- `PUT /api/categories/{{id}}`
- `DELETE /api/categories/{{id}}`
- `GET /api/products`
- `GET /api/products/{{id}}`
- `POST /api/products`
- `PUT /api/products/{{id}}`
- `DELETE /api/products/{{id}}`

## Portas e acessos

{chr(10).join(outputs)}

## Credenciais iniciais

{chr(10).join(creds)}
{note}

## Onde alterar

- Banco e dados iniciais: `database/init/01-schema.sql`
{backend_edit[context['BACKEND_KEY']]}
{frontend_edit[context['FRONTEND_KEY']]}
- Infra e portas: `docker-compose.yml` e `.env`

## Healthchecks

{chr(10).join(health_lines)}

## Como subir

```bash
docker compose up --build
```

## Arquivos importantes

- `docker-compose.yml`: orquestração principal
- `.env`: variáveis ativas do ambiente
- `.env.example`: cópia de referência das variáveis
- `database/init/01-schema.sql`: criação das tabelas e carga inicial
- `backend/`: API escolhida
- `frontend/`: interface escolhida

## Resumo de configuração

- O backend recebe `DB_CLIENT` para adaptar a conexão entre MySQL e Oracle.
- Os drivers do banco correspondente são instalados no backend gerado.
- Os dados e scripts são gravados em UTF-8.
- Para MySQL, o servidor sobe com `utf8mb4` e `utf8mb4_unicode_ci`.
- Quando o backend for `nenhum`, o frontend é gerado desacoplado da API.
- Quando o frontend for `nenhum`, o laboratório fica orientado a backend e banco.
'''


def print_summary(context: dict, destination: Path):
    section('Resumo final')
    print(f"  Projeto:        {context['PROJECT_SLUG']}")
    print(f"  Descrição:      {context['PROJECT_DESCRIPTION']}")
    print(f"  Banco:          {context['DB_LABEL']}")
    print(f"  Backend:        {context['BACKEND_LABEL']}")
    print(f"  Frontend:       {context['FRONTEND_LABEL']}")
    print(f"  Pasta gerada:   {destination.resolve()}")

    section('Acesso aos servidores do ambiente')
    if context['BACKEND_KEY'] != 'none':
        print(f"  Backend API:         http://localhost:{context['BACKEND_PORT']}")
    if context['FRONTEND_KEY'] != 'none':
        print(f"  Frontend:            http://localhost:{context['FRONTEND_PORT']}")
    print('  Banco de dados:')
    print('    Host:              localhost')
    print(f"    Porta:             {context['DB_PORT']}")
    print(f"    Tipo:              {context['DB_KEY']}")
    if context['DB_KEY'] == 'mysql':
        print(f"    Database:          {context['MYSQL_DATABASE']}")
        print(f"  phpMyAdmin:          http://localhost:{context['DB_ADMIN_PORT']}")
    else:
        print('    Service name:      FREEPDB1')
        print(f"  SQL Developer Web:   http://localhost:{context['DB_ADMIN_PORT']}")

    print('\n  Credenciais:')
    if context['DB_KEY'] == 'mysql':
        print(f"    - root / {context['MYSQL_ROOT_PASSWORD']}")
        print(f"    - {context['MYSQL_USER']} / {context['MYSQL_PASSWORD']}")
        print(f"    - database: {context['MYSQL_DATABASE']}")
    else:
        print(f"    - SYS/SYSTEM password: {context['ORACLE_PASSWORD']}")
        print(f"    - {context['ORACLE_APP_USER']} / {context['ORACLE_APP_PASSWORD']}")
        print('    - service: FREEPDB1')

    print('\n  Configurado:')
    print('    - README do projeto gerado')
    print('    - docker-compose dinâmico')
    print('    - schema inicial das duas tabelas')
    print('    - variáveis de conexão por banco')
    print('    - arquivo .env gerado automaticamente')
    print('    - drivers do banco no backend')

    print('\n  Próximos passos:')
    print(f'    cd {destination}')
    print('    docker compose up --build')


def build_schema(context: dict) -> str:
    if context['DB_KEY'] == 'mysql':
        database_name = context.get('MYSQL_DATABASE', 'labdb')
        return f'''SET NAMES utf8mb4;
ALTER DATABASE {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  description VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  category_id INT NOT NULL,
  name VARCHAR(120) NOT NULL,
  price DECIMAL(10,2) NOT NULL DEFAULT 0,
  stock INT NOT NULL DEFAULT 0,
  CONSTRAINT fk_products_category
    FOREIGN KEY (category_id) REFERENCES categories(id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO categories (name, description) VALUES
('Eletrônicos', 'Produtos eletrônicos em geral'),
('Livros', 'Livros físicos e digitais');

INSERT INTO products (category_id, name, price, stock) VALUES
(1, 'Mouse USB', 59.90, 10),
(1, 'Teclado Mecânico', 249.90, 5),
(2, 'Algoritmos em Prática', 89.90, 20);
'''
    oracle_user = context.get('ORACLE_APP_USER', 'LABUSER')
    return f'''WHENEVER SQLERROR EXIT SQL.SQLCODE;

ALTER SESSION SET CONTAINER = FREEPDB1;
ALTER SESSION SET CURRENT_SCHEMA = {oracle_user};

CREATE TABLE categories (
  id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  name VARCHAR2(120) NOT NULL,
  description VARCHAR2(255)
);

CREATE TABLE products (
  id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  category_id NUMBER NOT NULL,
  name VARCHAR2(120) NOT NULL,
  price NUMBER(10,2) DEFAULT 0 NOT NULL,
  stock NUMBER DEFAULT 0 NOT NULL,
  CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories(id)
);

INSERT INTO categories (name, description) VALUES ('Eletrônicos', 'Produtos eletrônicos em geral');
INSERT INTO categories (name, description) VALUES ('Livros', 'Livros físicos e digitais');

INSERT INTO products (category_id, name, price, stock) VALUES (1, 'Mouse USB', 59.90, 10);
INSERT INTO products (category_id, name, price, stock) VALUES (1, 'Teclado Mecânico', 249.90, 5);
INSERT INTO products (category_id, name, price, stock) VALUES (2, 'Algoritmos em Prática', 89.90, 20);

COMMIT;
'''


def main():
    if any(arg in {'-h', '--help'} for arg in sys.argv[1:]):
        print(HELP_TEXT)
        return

    banner()
    description, slug = ask_description()
    db_key, db_label = choose('Escolha o banco de dados', DATABASES)
    backend_key, backend_label = choose('Escolha o backend', BACKENDS)
    frontend_key, frontend_label = choose('Escolha o frontend', FRONTENDS)

    backend_port = 8000
    frontend_port = 3000
    db_port = 3306 if db_key == 'mysql' else 1521
    db_admin_port = 8080

    section('Portas fixas do ambiente')
    if backend_key != 'none':
        print(f'  Backend API:         {backend_port}')
    if frontend_key != 'none':
        print(f'  Frontend:            {frontend_port}')
    print(f'  Banco ({db_key}):        {db_port}')
    if db_key == 'mysql':
        print(f'  phpMyAdmin:          {db_admin_port}')
    else:
        print(f'  SQL Developer Web:   {db_admin_port}')

    destination = OUTPUT_DIR / slug
    existing_env = read_env_file(destination / '.env') if destination.exists() else {}

    if destination.exists() and not ask_yes_no(f'A pasta {destination} já existe. Deseja sobrescrever', True):
        print('Operação cancelada.')
        return
    if destination.exists():
        shutil.rmtree(destination)

    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'database' / 'init').mkdir(parents=True, exist_ok=True)

    context = build_default_context(
        description=description,
        slug=slug,
        db_key=db_key,
        db_label=db_label,
        backend_key=backend_key,
        backend_label=backend_label,
        frontend_key=frontend_key,
        frontend_label=frontend_label,
        backend_port=backend_port,
        frontend_port=frontend_port,
        db_port=db_port,
        db_admin_port=db_admin_port,
    )
    context = preserve_existing_credentials(context, existing_env)

    (destination / '.gitignore').write_text('node_modules\n.env\ndist\ncoverage\n__pycache__\n*.pyc\nvendor\ntarget\n', encoding='utf-8')
    env_text = build_env(context)
    (destination / '.env.example').write_text(env_text, encoding='utf-8')
    (destination / '.env').write_text(env_text, encoding='utf-8')
    (destination / 'docker-compose.yml').write_text(build_compose(context), encoding='utf-8')
    (destination / 'database' / 'init' / '01-schema.sql').write_text(build_schema(context), encoding='utf-8')
    (destination / 'README.md').write_text(project_readme(context), encoding='utf-8')

    if backend_key != 'none':
        copy_tree(TEMPLATES / 'backends' / backend_key, destination / 'backend')
    else:
        (destination / 'backend').mkdir(exist_ok=True)
        (destination / 'backend' / 'README.md').write_text('# Sem backend\n\nEste laboratório foi gerado sem backend.\n', encoding='utf-8')

    if frontend_key != 'none':
        copy_tree(TEMPLATES / 'frontends' / frontend_key, destination / 'frontend')
    else:
        (destination / 'frontend').mkdir(exist_ok=True)
        (destination / 'frontend' / 'README.md').write_text('# Sem frontend\n\nEste laboratório foi gerado sem frontend.\n', encoding='utf-8')

    render_all(destination, context)
    print_summary(context, destination)


if __name__ == '__main__':
    main()
