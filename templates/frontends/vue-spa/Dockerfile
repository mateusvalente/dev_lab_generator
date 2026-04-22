FROM node:22-alpine
RUN apk add --no-cache curl
WORKDIR /app
CMD ["sh", "-c", "npm install && npm run dev -- --host 0.0.0.0 --port ${PORT:-3000}"]
