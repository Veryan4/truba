FROM node:14 as builder

WORKDIR /app
COPY ./web/package.json /app

ENV NODE_OPTIONS=--max_old_space_size=512

RUN npm i

COPY ./web/ /app

ARG ENVIRONMENT=develop

RUN npm run "build-"$ENVIRONMENT

FROM fholzer/nginx-brotli:v1.18.0

## Remove default nginx website
RUN rm -rf /usr/share/nginx/html/*

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

COPY ./web/nginx/frontend.conf /etc/nginx/conf.d/frontend.conf
COPY ./web/nginx/nginx.conf /etc/nginx/nginx.conf

CMD ["nginx"]