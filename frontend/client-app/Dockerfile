# 1) Build Vue (Vite) app
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VUE_APP_API_BASE=
ENV VUE_APP_API_BASE=${VUE_APP_API_BASE}
RUN npm run build

# 2) Serve with Nginx and proxy API to backend service
FROM nginx:1.25-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY ./deploy/nginx.conf /etc/nginx/conf.d/default.conf
# SPA static/media volumes will be mounted from compose
EXPOSE 80
