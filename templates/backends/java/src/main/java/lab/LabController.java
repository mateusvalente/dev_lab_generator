package lab;

import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api")
public class LabController {
    private final JdbcTemplate jdbc;

    public LabController(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    private Map<String, Object> upperCaseKeys(Map<String, Object> input) {
        Map<String, Object> output = new LinkedHashMap<>();
        input.forEach((key, value) -> output.put(key.toUpperCase(), value));
        return output;
    }

    private List<Map<String, Object>> upperCaseRows(List<Map<String, Object>> rows) {
        return rows.stream().map(this::upperCaseKeys).collect(Collectors.toList());
    }

    private Object bodyValue(Map<String, Object> body, String key) {
        return body.containsKey(key) ? body.get(key) : body.get(key.toUpperCase());
    }

    @GetMapping("/health")
    public Map<String, Object> health() {
        Integer categories = jdbc.queryForObject("SELECT COUNT(*) FROM categories", Integer.class);
        return Map.of(
                "STATUS", "ok",
                "DB_CLIENT", "connected",
                "CATEGORIES", categories == null ? 0 : categories
        );
    }

    @GetMapping("/categories")
    public List<Map<String, Object>> categories() {
        return upperCaseRows(jdbc.queryForList("SELECT id, name, description FROM categories ORDER BY id"));
    }

    @GetMapping("/categories/{id}")
    public ResponseEntity<?> category(@PathVariable Integer id) {
        var rows = upperCaseRows(jdbc.queryForList("SELECT id, name, description FROM categories WHERE id = ?", id));
        return rows.isEmpty() ? ResponseEntity.notFound().build() : ResponseEntity.ok(rows.get(0));
    }

    @PostMapping("/categories")
    public ResponseEntity<?> createCategory(@RequestBody Map<String, Object> body) {
        jdbc.update("INSERT INTO categories(name, description) VALUES (?, ?)", bodyValue(body, "name"), bodyValue(body, "description"));
        Integer id = jdbc.queryForObject("SELECT MAX(id) FROM categories", Integer.class);
        return ResponseEntity.status(201).body(Map.of("ID", id));
    }

    @PutMapping("/categories/{id}")
    public Map<String, Object> updateCategory(@PathVariable Integer id, @RequestBody Map<String, Object> body) {
        jdbc.update("UPDATE categories SET name = ?, description = ? WHERE id = ?", bodyValue(body, "name"), bodyValue(body, "description"), id);
        return Map.of("UPDATED", true);
    }

    @DeleteMapping("/categories/{id}")
    public ResponseEntity<?> deleteCategory(@PathVariable Integer id) {
        jdbc.update("DELETE FROM categories WHERE id = ?", id);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/products")
    public List<Map<String, Object>> products() {
        return upperCaseRows(jdbc.queryForList("SELECT p.id, p.category_id, p.name, p.price, p.stock, c.name AS category_name FROM products p JOIN categories c ON c.id = p.category_id ORDER BY p.id"));
    }

    @GetMapping("/products/{id}")
    public ResponseEntity<?> product(@PathVariable Integer id) {
        var rows = upperCaseRows(jdbc.queryForList("SELECT id, category_id, name, price, stock FROM products WHERE id = ?", id));
        return rows.isEmpty() ? ResponseEntity.notFound().build() : ResponseEntity.ok(rows.get(0));
    }

    @PostMapping("/products")
    public ResponseEntity<?> createProduct(@RequestBody Map<String, Object> body) {
        jdbc.update(
                "INSERT INTO products(category_id, name, price, stock) VALUES (?, ?, ?, ?)",
                bodyValue(body, "category_id"),
                bodyValue(body, "name"),
                new BigDecimal(String.valueOf(bodyValue(body, "price"))),
                bodyValue(body, "stock")
        );
        Integer id = jdbc.queryForObject("SELECT MAX(id) FROM products", Integer.class);
        return ResponseEntity.status(201).body(Map.of("ID", id));
    }

    @PutMapping("/products/{id}")
    public Map<String, Object> updateProduct(@PathVariable Integer id, @RequestBody Map<String, Object> body) {
        jdbc.update(
                "UPDATE products SET category_id = ?, name = ?, price = ?, stock = ? WHERE id = ?",
                bodyValue(body, "category_id"),
                bodyValue(body, "name"),
                new BigDecimal(String.valueOf(bodyValue(body, "price"))),
                bodyValue(body, "stock"),
                id
        );
        return Map.of("UPDATED", true);
    }

    @DeleteMapping("/products/{id}")
    public ResponseEntity<?> deleteProduct(@PathVariable Integer id) {
        jdbc.update("DELETE FROM products WHERE id = ?", id);
        return ResponseEntity.noContent().build();
    }
}
