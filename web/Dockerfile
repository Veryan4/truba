FROM node:22 as builder

WORKDIR /app
COPY ./web/package.json /app

ENV NODE_OPTIONS=--max_old_space_size=512

RUN npm i

COPY ./web/ /app

ARG ENVIRONMENT=develop

RUN npm run "build-"$ENVIRONMENT

FROM fholzer/nginx-brotli:v1.28.0

## Remove default nginx website
RUN rm -rf /usr/share/nginx/html/*

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

COPY ./web/nginx/frontend.conf /etc/nginx/conf.d/frontend.conf
COPY ./web/nginx/nginx.conf /etc/nginx/nginx.conf

ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
