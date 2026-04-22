
package lab;

import com.zaxxer.hikari.HikariDataSource;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.env.Environment;

import javax.sql.DataSource;

@Configuration
public class DataSourceConfig {
    @Bean
    public DataSource dataSource(Environment env) {
        String client = env.getProperty("DB_CLIENT", "mysql");
        String host = env.getProperty("DB_HOST", "db");
        String port = env.getProperty("DB_PORT", "3306");
        String db = env.getProperty("DB_NAME", "labdb");
        String user = env.getProperty("DB_USER", "labuser");
        String password = env.getProperty("DB_PASSWORD", "labpass");

        HikariDataSource ds = new HikariDataSource();
        ds.setUsername(user);
        ds.setPassword(password);
        if ("oracle".equalsIgnoreCase(client)) {
            ds.setDriverClassName("oracle.jdbc.OracleDriver");
            ds.setJdbcUrl("jdbc:oracle:thin:@//" + host + ":" + port + "/" + db);
        } else {
            ds.setDriverClassName("com.mysql.cj.jdbc.Driver");
            ds.setJdbcUrl("jdbc:mysql://" + host + ":" + port + "/" + db + "?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC&useUnicode=true&characterEncoding=UTF-8&connectionCollation=utf8mb4_unicode_ci");
        }
        return ds;
    }
}
