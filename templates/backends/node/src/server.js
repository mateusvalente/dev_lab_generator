import express from 'express';
import cors from 'cors';
import mysql from 'mysql2/promise';
import oracledb from 'oracledb';

const app = express();
const port = Number(process.env.PORT || 8000);
const dbClient = (process.env.DB_CLIENT || 'mysql').toLowerCase();

app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With', 'Accept', 'Origin'],
  exposedHeaders: ['Content-Type'],
}));
app.options('*', cors());
app.use(express.json());

let mysqlPool = null;

function upperCaseKeys(value) {
  if (Array.isArray(value)) return value.map(upperCaseKeys);
  if (!value || typeof value !== 'object') return value;
  return Object.fromEntries(Object.entries(value).map(([key, item]) => [key.toUpperCase(), upperCaseKeys(item)]));
}

function bodyValue(body, field) {
  return body?.[field] ?? body?.[field.toUpperCase()];
}

function normalizeRows(rows) {
  return (rows || []).map((row) => upperCaseKeys(row));
}

async function getMysqlPool() {
  if (!mysqlPool) {
    mysqlPool = mysql.createPool({
      host: process.env.DB_HOST || 'db',
      port: Number(process.env.DB_PORT || 3306),
      user: process.env.DB_USER || 'labuser',
      password: process.env.DB_PASSWORD || 'labpass',
      database: process.env.DB_NAME || 'labdb',
      charset: 'utf8mb4',
    });
  }
  return mysqlPool;
}

async function query(sql, params = []) {
  if (dbClient === 'oracle') {
    const conn = await oracledb.getConnection({
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      connectString: `${process.env.DB_HOST}:${process.env.DB_PORT}/${process.env.DB_NAME}`,
    });
    try {
      const result = await conn.execute(sql, params, { autoCommit: true, outFormat: oracledb.OUT_FORMAT_OBJECT });
      return { rows: normalizeRows(result.rows) };
    } finally {
      await conn.close();
    }
  }

  const pool = await getMysqlPool();
  const [rows] = await pool.query(sql, params);
  return { rows: normalizeRows(rows) };
}

function wrap(handler) {
  return (req, res) => Promise.resolve(handler(req, res)).catch((err) => {
    console.error(err);
    res.status(500).json({ ERROR: 'Internal error', DETAILS: String(err.message || err) });
  });
}

app.get('/api/health', wrap(async (_, res) => {
  const sql = dbClient === 'oracle'
    ? 'SELECT COUNT(*) AS TOTAL FROM categories'
    : 'SELECT COUNT(*) AS TOTAL FROM categories';
  const result = await query(sql);
  const row = result.rows[0] || {};
  res.json({
    STATUS: 'ok',
    DB_CLIENT: dbClient,
    CATEGORIES: row.TOTAL ?? 0,
  });
}));

app.get('/api/categories', wrap(async (_, res) => {
  const result = await query('SELECT id, name, description FROM categories ORDER BY id');
  res.json(result.rows);
}));

app.get('/api/categories/:id', wrap(async (req, res) => {
  const sql = dbClient === 'oracle' ? 'SELECT id, name, description FROM categories WHERE id = :1' : 'SELECT id, name, description FROM categories WHERE id = ?';
  const result = await query(sql, [Number(req.params.id)]);
  const row = result.rows[0];
  if (!row) return res.status(404).json({ ERROR: 'Not found' });
  res.json(row);
}));

app.post('/api/categories', wrap(async (req, res) => {
  const name = bodyValue(req.body, 'name') ?? '';
  const description = bodyValue(req.body, 'description') ?? null;
  if (dbClient === 'oracle') {
    await query('INSERT INTO categories(name, description) VALUES (:1, :2)', [name, description]);
    const idResult = await query('SELECT MAX(id) AS ID FROM categories');
    return res.status(201).json({ ID: idResult.rows[0]?.ID ?? 0 });
  }
  const pool = await getMysqlPool();
  const [result] = await pool.query('INSERT INTO categories(name, description) VALUES (?, ?)', [name, description]);
  res.status(201).json({ ID: result.insertId });
}));

app.put('/api/categories/:id', wrap(async (req, res) => {
  const name = bodyValue(req.body, 'name') ?? '';
  const description = bodyValue(req.body, 'description') ?? null;
  const sql = dbClient === 'oracle'
    ? 'UPDATE categories SET name = :1, description = :2 WHERE id = :3'
    : 'UPDATE categories SET name = ?, description = ? WHERE id = ?';
  await query(sql, [name, description, Number(req.params.id)]);
  res.json({ UPDATED: true });
}));

app.delete('/api/categories/:id', wrap(async (req, res) => {
  const sql = dbClient === 'oracle' ? 'DELETE FROM categories WHERE id = :1' : 'DELETE FROM categories WHERE id = ?';
  await query(sql, [Number(req.params.id)]);
  res.status(204).send();
}));

app.get('/api/products', wrap(async (_, res) => {
  const result = await query('SELECT p.id, p.category_id, p.name, p.price, p.stock, c.name AS category_name FROM products p JOIN categories c ON c.id = p.category_id ORDER BY p.id');
  res.json(result.rows);
}));

app.get('/api/products/:id', wrap(async (req, res) => {
  const sql = dbClient === 'oracle'
    ? 'SELECT id, category_id, name, price, stock FROM products WHERE id = :1'
    : 'SELECT id, category_id, name, price, stock FROM products WHERE id = ?';
  const result = await query(sql, [Number(req.params.id)]);
  const row = result.rows[0];
  if (!row) return res.status(404).json({ ERROR: 'Not found' });
  res.json(row);
}));

app.post('/api/products', wrap(async (req, res) => {
  const categoryId = Number(bodyValue(req.body, 'category_id') ?? 0);
  const name = bodyValue(req.body, 'name') ?? '';
  const price = Number(bodyValue(req.body, 'price') ?? 0);
  const stock = Number(bodyValue(req.body, 'stock') ?? 0);
  if (dbClient === 'oracle') {
    await query('INSERT INTO products(category_id, name, price, stock) VALUES (:1, :2, :3, :4)', [categoryId, name, price, stock]);
    const idResult = await query('SELECT MAX(id) AS ID FROM products');
    return res.status(201).json({ ID: idResult.rows[0]?.ID ?? 0 });
  }
  const pool = await getMysqlPool();
  const [result] = await pool.query('INSERT INTO products(category_id, name, price, stock) VALUES (?, ?, ?, ?)', [categoryId, name, price, stock]);
  res.status(201).json({ ID: result.insertId });
}));

app.put('/api/products/:id', wrap(async (req, res) => {
  const categoryId = Number(bodyValue(req.body, 'category_id') ?? 0);
  const name = bodyValue(req.body, 'name') ?? '';
  const price = Number(bodyValue(req.body, 'price') ?? 0);
  const stock = Number(bodyValue(req.body, 'stock') ?? 0);
  const sql = dbClient === 'oracle'
    ? 'UPDATE products SET category_id = :1, name = :2, price = :3, stock = :4 WHERE id = :5'
    : 'UPDATE products SET category_id = ?, name = ?, price = ?, stock = ? WHERE id = ?';
  await query(sql, [categoryId, name, price, stock, Number(req.params.id)]);
  res.json({ UPDATED: true });
}));

app.delete('/api/products/:id', wrap(async (req, res) => {
  const sql = dbClient === 'oracle' ? 'DELETE FROM products WHERE id = :1' : 'DELETE FROM products WHERE id = ?';
  await query(sql, [Number(req.params.id)]);
  res.status(204).send();
}));

app.listen(port, '0.0.0.0', () => console.log(`Backend Node rodando na porta ${port}`));
