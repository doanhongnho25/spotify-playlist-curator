# Pin to specific Node version to avoid breaking changes
FROM node:18.20.2-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]