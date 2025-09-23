FROM nginx:latest

RUN rm /etc/nginx/conf.d/default.conf

COPY ./notes-app.conf /etc/nginx/conf.d/notes-app.conf
COPY ./frontend/dist /usr/share/nginx/html

EXPOSE 80
EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]
