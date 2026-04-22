# {{PROJECT_NAME}}

Projeto gerado pelo **Dev Lab Generator**.

## Stack escolhida
- Backend: **{{BACKEND_NAME}}**
- Frontend: **{{FRONTEND_NAME}}**
- Banco: **MySQL + phpMyAdmin**

## Subir o ambiente

Copie o arquivo de ambiente:

```bash
cp .env.example .env
```

Depois execute:

```bash
docker compose up --build
```

## Endereços padrão

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- phpMyAdmin: `http://localhost:8080`

## Rotas REST

### Categories
- `GET /api/categories`
- `GET /api/categories/{id}`
- `POST /api/categories`
- `PUT /api/categories/{id}`
- `DELETE /api/categories/{id}`

### Products
- `GET /api/products`
- `GET /api/products/{id}`
- `POST /api/products`
- `PUT /api/products/{id}`
- `DELETE /api/products/{id}`
