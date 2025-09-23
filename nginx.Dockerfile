FROM node:20 AS build
WORKDIR /app

COPY ./frontend/package*.json ./
RUN npm install

COPY ./frontend/ ./
RUN npm run build

FROM nginx:latest
RUN rm /etc/nginx/conf.d/default.conf

COPY ./notes-app.conf /etc/nginx/conf.d/notes-app.conf

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]