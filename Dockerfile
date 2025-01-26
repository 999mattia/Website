# Stage 1: Build the Angular app
FROM node:20 AS build

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the Angular app for production
RUN npm run build --prod

# Stage 2: Serve the app with Nginx
FROM nginx:latest AS ngx

# Copy the built Angular app to Nginx's html directory
COPY --from=build /app/dist/website/browser/ /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
