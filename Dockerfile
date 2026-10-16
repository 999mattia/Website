FROM nginx:alpine
RUN sed -i '1i load_module modules/ngx_http_js_module.so;' /etc/nginx/nginx.conf
COPY njs /etc/nginx/njs
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
