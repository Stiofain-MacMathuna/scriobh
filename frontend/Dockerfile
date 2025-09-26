# Stage 1: Build
FROM node:20-alpine AS build

WORKDIR /app

# Accept build-time environment (default to production)
ARG ENV=production
ENV NODE_ENV=$ENV

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Copy correct env file based on build arg
COPY .env.$ENV .env.local

# Build the frontend
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:stable-alpine

# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]