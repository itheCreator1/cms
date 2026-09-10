FROM node:24-slim

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./

CMD ["npm", "run", "dev"]
