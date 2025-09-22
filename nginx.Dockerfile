FROM nginx:stable-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY ./notes-app.conf /etc/nginx/conf.d/notes-app.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
