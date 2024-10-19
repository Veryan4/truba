## Core Api

This service manages all back-end communication. There is a back-end facing (core.go), front-end facing (coreui.go), cronjob'd (push.gp), and async (worker.go) copy of the same image.

### Running

You need to install the dependencies
```
go mod download
```
You then need to generate the shared models
```
go run ./tools/tools.go
```

After adding the required .env values, you can then run one of the services with `go run ./cmd/<name-of-service>/<name-of-service>.go`

Available services: core.go, coreui.go, push.go, or worker.go


### Build

```
docker-compose build core
```
