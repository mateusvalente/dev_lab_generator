package lab;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import java.io.IOException;
import java.math.BigDecimal;
import java.sql.SQLException;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class ApiServlet extends HttpServlet {
    private final Database database;
    private final ObjectMapper json = new ObjectMapper();

    public ApiServlet(Database database) {
        this.database = database;
    }

    @Override
    protected void doOptions(HttpServletRequest request, HttpServletResponse response) {
        addCors(response);
        response.setStatus(HttpServletResponse.SC_NO_CONTENT);
    }

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        handle(request, response);
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
        handle(request, response);
    }

    @Override
    protected void doPut(HttpServletRequest request, HttpServletResponse response) throws IOException {
        handle(request, response);
    }

    @Override
    protected void doDelete(HttpServletRequest request, HttpServletResponse response) throws IOException {
        handle(request, response);
    }

    private void handle(HttpServletRequest request, HttpServletResponse response) throws IOException {
        addCors(response);
        response.setCharacterEncoding("UTF-8");

        try {
            route(request, response);
        } catch (IllegalArgumentException error) {
            writeJson(response, HttpServletResponse.SC_BAD_REQUEST, Map.of("ERROR", error.getMessage()));
        } catch (SQLException error) {
            writeJson(response, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, Map.of("ERROR", error.getMessage()));
        }
    }

    private void route(HttpServletRequest request, HttpServletResponse response) throws IOException, SQLException {
        String method = request.getMethod();
        String path = request.getPathInfo() == null ? "/" : request.getPathInfo();

        if ("GET".equals(method) && "/health".equals(path)) {
            Integer categories = database.intValue("SELECT COUNT(*) FROM categories");
            writeJson(response, HttpServletResponse.SC_OK, Map.of(
                    "STATUS", "ok",
                    "DB_CLIENT", database.client(),
                    "CATEGORIES", categories == null ? 0 : categories
            ));
            return;
        }

        if ("GET".equals(method) && "/categories".equals(path)) {
            writeJson(response, HttpServletResponse.SC_OK,
                    database.query("SELECT id, name, description FROM categories ORDER BY id"));
            return;
        }

        if ("POST".equals(method) && "/categories".equals(path)) {
            Map<String, Object> body = readBody(request);
            database.update(
                    "INSERT INTO categories(name, description) VALUES (?, ?)",
                    bodyValue(body, "name"),
                    bodyValue(body, "description")
            );
            Integer id = database.intValue("SELECT MAX(id) FROM categories");
            writeJson(response, HttpServletResponse.SC_CREATED, Map.of("ID", id));
            return;
        }

        if (path.matches("/categories/\\d+")) {
            Integer id = pathId(path);
            handleCategoryById(method, id, request, response);
            return;
        }

        if ("GET".equals(method) && "/products".equals(path)) {
            writeJson(response, HttpServletResponse.SC_OK,
                    database.query("SELECT p.id, p.category_id, p.name, p.price, p.stock, c.name AS category_name FROM products p JOIN categories c ON c.id = p.category_id ORDER BY p.id"));
            return;
        }

        if ("POST".equals(method) && "/products".equals(path)) {
            Map<String, Object> body = readBody(request);
            database.update(
                    "INSERT INTO products(category_id, name, price, stock) VALUES (?, ?, ?, ?)",
                    bodyValue(body, "category_id"),
                    bodyValue(body, "name"),
                    decimalValue(body, "price"),
                    bodyValue(body, "stock")
            );
            Integer id = database.intValue("SELECT MAX(id) FROM products");
            writeJson(response, HttpServletResponse.SC_CREATED, Map.of("ID", id));
            return;
        }

        if (path.matches("/products/\\d+")) {
            Integer id = pathId(path);
            handleProductById(method, id, request, response);
            return;
        }

        writeJson(response, HttpServletResponse.SC_NOT_FOUND, Map.of("ERROR", "Rota nao encontrada"));
    }

    private void handleCategoryById(String method, Integer id, HttpServletRequest request, HttpServletResponse response)
            throws IOException, SQLException {
        if ("GET".equals(method)) {
            List<Map<String, Object>> rows = database.query("SELECT id, name, description FROM categories WHERE id = ?", id);
            writeRowOrNotFound(response, rows);
            return;
        }

        if ("PUT".equals(method)) {
            Map<String, Object> body = readBody(request);
            database.update(
                    "UPDATE categories SET name = ?, description = ? WHERE id = ?",
                    bodyValue(body, "name"),
                    bodyValue(body, "description"),
                    id
            );
            writeJson(response, HttpServletResponse.SC_OK, Map.of("UPDATED", true));
            return;
        }

        if ("DELETE".equals(method)) {
            database.update("DELETE FROM categories WHERE id = ?", id);
            response.setStatus(HttpServletResponse.SC_NO_CONTENT);
            return;
        }

        writeJson(response, HttpServletResponse.SC_METHOD_NOT_ALLOWED, Map.of("ERROR", "Metodo nao permitido"));
    }

    private void handleProductById(String method, Integer id, HttpServletRequest request, HttpServletResponse response)
            throws IOException, SQLException {
        if ("GET".equals(method)) {
            List<Map<String, Object>> rows = database.query("SELECT id, category_id, name, price, stock FROM products WHERE id = ?", id);
            writeRowOrNotFound(response, rows);
            return;
        }

        if ("PUT".equals(method)) {
            Map<String, Object> body = readBody(request);
            database.update(
                    "UPDATE products SET category_id = ?, name = ?, price = ?, stock = ? WHERE id = ?",
                    bodyValue(body, "category_id"),
                    bodyValue(body, "name"),
                    decimalValue(body, "price"),
                    bodyValue(body, "stock"),
                    id
            );
            writeJson(response, HttpServletResponse.SC_OK, Map.of("UPDATED", true));
            return;
        }

        if ("DELETE".equals(method)) {
            database.update("DELETE FROM products WHERE id = ?", id);
            response.setStatus(HttpServletResponse.SC_NO_CONTENT);
            return;
        }

        writeJson(response, HttpServletResponse.SC_METHOD_NOT_ALLOWED, Map.of("ERROR", "Metodo nao permitido"));
    }

    private Map<String, Object> readBody(HttpServletRequest request) throws IOException {
        if (request.getInputStream() == null) {
            return new LinkedHashMap<>();
        }
        return json.readValue(request.getInputStream(), new TypeReference<>() {});
    }

    private Object bodyValue(Map<String, Object> body, String key) {
        Object value = body.containsKey(key) ? body.get(key) : body.get(key.toUpperCase());
        if (value == null) {
            throw new IllegalArgumentException("Campo obrigatorio ausente: " + key);
        }
        return value;
    }

    private BigDecimal decimalValue(Map<String, Object> body, String key) {
        return new BigDecimal(String.valueOf(bodyValue(body, key)));
    }

    private Integer pathId(String path) {
        return Integer.parseInt(path.substring(path.lastIndexOf('/') + 1));
    }

    private void writeRowOrNotFound(HttpServletResponse response, List<Map<String, Object>> rows) throws IOException {
        if (rows.isEmpty()) {
            writeJson(response, HttpServletResponse.SC_NOT_FOUND, Map.of("ERROR", "Registro nao encontrado"));
        } else {
            writeJson(response, HttpServletResponse.SC_OK, rows.get(0));
        }
    }

    private void writeJson(HttpServletResponse response, int status, Object payload) throws IOException {
        response.setStatus(status);
        response.setContentType("application/json");
        json.writeValue(response.getOutputStream(), payload);
    }

    private void addCors(HttpServletResponse response) {
        response.setHeader("Access-Control-Allow-Origin", "*");
        response.setHeader("Access-Control-Allow-Methods", "GET,POST,PUT,PATCH,DELETE,OPTIONS");
        response.setHeader("Access-Control-Allow-Headers", "Content-Type,Authorization");
    }
}
