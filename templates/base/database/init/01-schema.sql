CREATE TABLE IF NOT EXISTS categories (
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
