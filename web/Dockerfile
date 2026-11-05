# [stage__build]-[BEGIN]================================================

FROM node:22.23.4-alpine AS build

ARG WORKDIR=/app

WORKDIR ${WORKDIR}

COPY package.json package-lock.json .npmrc ${WORKDIR}/

RUN npm ci

COPY . .

ARG VITE_API_URL

RUN npm run build

# [stage__build]-[END]==================================================


# [stage__final]-[BEGIN]================================================

FROM nginx:1.30.6-alpine AS final

ARG WORKDIR=/app

COPY --from=build ${WORKDIR}/dist /usr/share/nginx/html

COPY nginx.conf  /etc/nginx/conf.d/default.conf

# [stage__final]-[END]==================================================
