package lab;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class Database {
    private final String client;
    private final String jdbcUrl;
    private final String user;
    private final String password;

    public Database() {
        this.client = env("DB_CLIENT", "mysql").toLowerCase();
        String host = env("DB_HOST", "db");
        String port = env("DB_PORT", "3306");
        String database = env("DB_NAME", "labdb");
        this.user = env("DB_USER", "labuser");
        this.password = env("DB_PASSWORD", "admin");

        if ("oracle".equals(client)) {
            this.jdbcUrl = "jdbc:oracle:thin:@//" + host + ":" + port + "/" + database;
        } else {
            this.jdbcUrl = "jdbc:mysql://" + host + ":" + port + "/" + database
                    + "?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC"
                    + "&useUnicode=true&characterEncoding=UTF-8&connectionCollation=utf8mb4_unicode_ci";
        }
    }

    public String client() {
        return client;
    }

    public Connection connection() throws SQLException {
        return DriverManager.getConnection(jdbcUrl, user, password);
    }

    public List<Map<String, Object>> query(String sql, Object... params) throws SQLException {
        try (Connection connection = connection();
             PreparedStatement statement = connection.prepareStatement(sql)) {
            bind(statement, params);
            try (ResultSet resultSet = statement.executeQuery()) {
                ResultSetMetaData metaData = resultSet.getMetaData();
                List<Map<String, Object>> rows = new ArrayList<>();

                while (resultSet.next()) {
                    Map<String, Object> row = new LinkedHashMap<>();
                    for (int index = 1; index <= metaData.getColumnCount(); index++) {
                        String label = metaData.getColumnLabel(index).toUpperCase();
                        row.put(label, resultSet.getObject(index));
                    }
                    rows.add(row);
                }

                return rows;
            }
        }
    }

    public int update(String sql, Object... params) throws SQLException {
        try (Connection connection = connection();
             PreparedStatement statement = connection.prepareStatement(sql)) {
            bind(statement, params);
            return statement.executeUpdate();
        }
    }

    public Integer intValue(String sql, Object... params) throws SQLException {
        List<Map<String, Object>> rows = query(sql, params);
        if (rows.isEmpty() || rows.get(0).isEmpty()) {
            return null;
        }
        Object value = rows.get(0).values().iterator().next();
        return value instanceof Number number ? number.intValue() : Integer.parseInt(String.valueOf(value));
    }

    private void bind(PreparedStatement statement, Object... params) throws SQLException {
        for (int index = 0; index < params.length; index++) {
            statement.setObject(index + 1, params[index]);
        }
    }

    private String env(String name, String fallback) {
        String value = System.getenv(name);
        return value == null || value.isBlank() ? fallback : value;
    }
}
