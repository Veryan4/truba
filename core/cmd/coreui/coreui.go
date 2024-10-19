package main

import (
	"log"
	"net/http"
	"os"

	"core/internal/controllers"
	"core/internal/tasks"

	"github.com/gorilla/mux"
	"go.opentelemetry.io/contrib/instrumentation/github.com/gorilla/mux/otelmux"
)

func main() {
	log.Printf("Started CoreUI Service")
	r := mux.NewRouter()
	queueClient := tasks.GetQueueConnection()
	r = controllers.PublicRoutes(r, queueClient)
	r = controllers.SecureRoutes(r, queueClient)
	r = controllers.SocketRoutes(r)
	if controllers.IsProd {
		r.Schemes("https", "wss")
	} else {
		r.Schemes("https", "http", "wss", "ws")
	}
	r.Use(otelmux.Middleware(os.Getenv("ENVIRONMENT") + "_coreui"))
	r.Use(controllers.LoggingMiddleware)
	r.Use(controllers.CORSMiddleware)
	// TODO look into brotli compression
	http.ListenAndServe(":"+os.Getenv("CORE_UI_PORT"), r)
}
