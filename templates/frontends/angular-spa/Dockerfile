FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["sh", "-c", "npm start -- --host 0.0.0.0 --port ${PORT:-3000}"]
