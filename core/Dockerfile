FROM golang:1.23-alpine AS build

WORKDIR /app

COPY ./core/go.mod ./
COPY ./core/go.sum ./
RUN go mod download

COPY ./core/ .
COPY ./schemas/ ../schemas/

RUN go run ./tools/tools.go

RUN mkdir build
RUN go build -C ./cmd/core/ -o ../../build
RUN go build -C ./cmd/coreui/ -o ../../build
RUN go build -C ./cmd/push/ -o ../../build
RUN go build -C ./cmd/worker/ -o ../../build

FROM alpine:latest

WORKDIR /app

RUN mkdir tmp
COPY --from=build /app/data .
COPY --from=build /app/build .

CMD ["/app/core"]
