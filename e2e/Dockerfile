FROM mcr.microsoft.com/playwright:v1.63.0-noble

WORKDIR /app/e2e

COPY e2e/package.json ./
RUN npm install --no-audit --no-fund

COPY e2e/ ./

CMD ["npm", "test"]
