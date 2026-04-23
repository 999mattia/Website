FROM hugomods/hugo:exts AS builder
WORKDIR /app
COPY . .
RUN hugo --minify

FROM nginx:alpine
COPY --from=builder /app/public /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]