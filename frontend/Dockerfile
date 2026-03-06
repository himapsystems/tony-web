FROM node:20-alpine

WORKDIR /app

# 1. Copia apenas os arquivos de pacotes primeiro
COPY package*.json ./

# 2. Instala as dependências dentro do ambiente Linux do Docker
RUN npm install

# 3. Copia o resto dos arquivos
COPY . .

# 4. FIX DE PERMISSÃO: Garante que o 'next' pode ser executado
RUN chmod +x node_modules/.bin/next

# 5. Build do Next.js
RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "start"]