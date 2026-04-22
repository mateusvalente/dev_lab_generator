FROM maven:3.9.9-eclipse-temurin-21
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
CMD ["sh", "-c", "mvn -q spring-boot:run -Dspring-boot.run.jvmArguments=\"-Dserver.port=${PORT:-8000}\""]
