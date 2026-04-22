<?php

ini_set('display_errors', 0);

header('Content-Type: application/json; charset=UTF-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With, Accept, Origin');
header('Access-Control-Expose-Headers: Content-Type');
header('Access-Control-Allow-Methods: GET,POST,PUT,PATCH,DELETE,OPTIONS');
header('Vary: Origin');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }

$dbClient = getenv('DB_CLIENT') ?: 'mysql';
$dbHost = getenv('DB_HOST') ?: 'db';
$dbPort = getenv('DB_PORT') ?: ($dbClient === 'oracle' ? '1521' : '3306');
$dbName = getenv('DB_NAME') ?: ($dbClient === 'oracle' ? 'FREEPDB1' : 'labdb');
$dbUser = getenv('DB_USER') ?: ($dbClient === 'oracle' ? 'LABUSER' : 'labuser');
$dbPassword = getenv('DB_PASSWORD') ?: 'labpass';

if ($dbClient === 'oracle') {
    respond([
        'ERROR' => 'Oracle is not yet supported by the PHP template.',
        'DB_CLIENT' => $dbClient,
    ], 501);
} else {
    $dsn = sprintf('mysql:host=%s;port=%s;dbname=%s;charset=utf8mb4', $dbHost, $dbPort, $dbName);
}

$pdo = new PDO($dsn, $dbUser, $dbPassword, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
$method = $_SERVER['REQUEST_METHOD'];
$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

function jsonBody() { return json_decode(file_get_contents('php://input'), true) ?: []; }
function respond($data, int $status = 200): void { http_response_code($status); if ($status !== 204) echo json_encode($data, JSON_UNESCAPED_UNICODE); exit; }
function notFound(): void { respond(['ERROR' => 'Not found'], 404); }
function bodyValue(array $body, string $field, $default = null) { return $body[$field] ?? $body[strtoupper($field)] ?? $default; }
function upperCaseKeys($value) {
    if (is_array($value)) {
        $isList = array_keys($value) === range(0, count($value) - 1);
        if ($isList) {
            return array_map('upperCaseKeys', $value);
        }
        $output = [];
        foreach ($value as $key => $item) {
            $output[strtoupper((string)$key)] = upperCaseKeys($item);
        }
        return $output;
    }
    return $value;
}
function p(string $sql): string {
    global $dbClient;
    if ($dbClient === 'oracle') {
        return preg_replace_callback('/\?/', function() { static $i = 0; $i++; return ':p' . $i; }, $sql);
    }
    return $sql;
}
function execStmt(PDO $pdo, string $sql, array $params = []) {
    global $dbClient;
    $stmt = $pdo->prepare(p($sql));
    if ($dbClient === 'oracle') {
        $i = 1; foreach ($params as $value) { $stmt->bindValue(':p'.$i, $value); $i++; }
        $stmt->execute();
    } else {
        $stmt->execute($params);
    }
    return $stmt;
}

if ($uri === '/health' && $method === 'GET') {
    if ($dbClient === 'oracle') {
        respond([
            'ERROR' => 'Oracle is not yet supported by the PHP template.',
            'DB_CLIENT' => $dbClient,
        ], 501);
    }
    $categories = (int)$pdo->query('SELECT COUNT(*) AS TOTAL FROM categories')->fetch(PDO::FETCH_ASSOC)['TOTAL'];
    respond([
        'STATUS' => 'ok',
        'DB_CLIENT' => $dbClient,
        'CATEGORIES' => $categories,
    ]);
}

if ($uri === '/api/categories' && $method === 'GET') {
    respond(upperCaseKeys($pdo->query('SELECT id, name, description FROM categories ORDER BY id')->fetchAll(PDO::FETCH_ASSOC)));
}
if (preg_match('#^/api/categories/(\d+)$#', $uri, $m) && $method === 'GET') {
    $item = execStmt($pdo, 'SELECT id, name, description FROM categories WHERE id = ?', [(int)$m[1]])->fetch(PDO::FETCH_ASSOC);
    $item ? respond(upperCaseKeys($item)) : notFound();
}
if ($uri === '/api/categories' && $method === 'POST') {
    $body = jsonBody();
    execStmt($pdo, 'INSERT INTO categories(name, description) VALUES (?, ?)', [bodyValue($body, 'name', ''), bodyValue($body, 'description')]);
    respond(['ID' => (int)$pdo->lastInsertId()], 201);
}
if (preg_match('#^/api/categories/(\d+)$#', $uri, $m) && $method === 'PUT') {
    $body = jsonBody();
    execStmt($pdo, 'UPDATE categories SET name = ?, description = ? WHERE id = ?', [bodyValue($body, 'name', ''), bodyValue($body, 'description'), (int)$m[1]]);
    respond(['UPDATED' => true]);
}
if (preg_match('#^/api/categories/(\d+)$#', $uri, $m) && $method === 'DELETE') {
    execStmt($pdo, 'DELETE FROM categories WHERE id = ?', [(int)$m[1]]);
    respond([], 204);
}
if ($uri === '/api/products' && $method === 'GET') {
    respond(upperCaseKeys($pdo->query('SELECT p.id, p.category_id, p.name, p.price, p.stock, c.name AS category_name FROM products p JOIN categories c ON c.id = p.category_id ORDER BY p.id')->fetchAll(PDO::FETCH_ASSOC)));
}
if (preg_match('#^/api/products/(\d+)$#', $uri, $m) && $method === 'GET') {
    $item = execStmt($pdo, 'SELECT id, category_id, name, price, stock FROM products WHERE id = ?', [(int)$m[1]])->fetch(PDO::FETCH_ASSOC);
    $item ? respond(upperCaseKeys($item)) : notFound();
}
if ($uri === '/api/products' && $method === 'POST') {
    $body = jsonBody();
    execStmt($pdo, 'INSERT INTO products(category_id, name, price, stock) VALUES (?, ?, ?, ?)', [bodyValue($body, 'category_id', 0), bodyValue($body, 'name', ''), bodyValue($body, 'price', 0), bodyValue($body, 'stock', 0)]);
    respond(['ID' => (int)$pdo->lastInsertId()], 201);
}
if (preg_match('#^/api/products/(\d+)$#', $uri, $m) && $method === 'PUT') {
    $body = jsonBody();
    execStmt($pdo, 'UPDATE products SET category_id = ?, name = ?, price = ?, stock = ? WHERE id = ?', [bodyValue($body, 'category_id', 0), bodyValue($body, 'name', ''), bodyValue($body, 'price', 0), bodyValue($body, 'stock', 0), (int)$m[1]]);
    respond(['UPDATED' => true]);
}
if (preg_match('#^/api/products/(\d+)$#', $uri, $m) && $method === 'DELETE') {
    execStmt($pdo, 'DELETE FROM products WHERE id = ?', [(int)$m[1]]);
    respond([], 204);
}
notFound();
