
package lab;

import org.apache.catalina.Context;
import org.apache.catalina.startup.Tomcat;

import java.io.File;

public class Application {
    public static void main(String[] args) {
        int port = Integer.parseInt(System.getenv().getOrDefault("PORT", "8000"));

        try {
            Tomcat tomcat = new Tomcat();
            tomcat.setPort(port);
            tomcat.getConnector();

            Context context = tomcat.addContext("", new File(".").getAbsolutePath());
            Tomcat.addServlet(context, "apiServlet", new ApiServlet(new Database()));
            context.addServletMappingDecoded("/api/*", "apiServlet");

            tomcat.start();
            System.out.println("Java Tomcat API em " + port);
            tomcat.getServer().await();
        } catch (Exception error) {
            error.printStackTrace();
            System.exit(1);
        }
    }
}
