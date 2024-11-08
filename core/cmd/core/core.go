package main

import (
	"log"
	"net/http"
	"os"
	"strings"

	"core/internal/controllers"
	"core/internal/tasks"

	"github.com/gorilla/mux"
	"go.opentelemetry.io/contrib/instrumentation/github.com/gorilla/mux/otelmux"
)

func main() {
	log.Printf("Started Core Service")
	r := mux.NewRouter()
	queueClient := tasks.GetQueueConnection()
	r = controllers.PrivateRoutes(r, queueClient)
	r.Use(controllers.LoggingMiddleware)
	r.Use(otelmux.Middleware(os.Getenv("ENVIRONMENT") + "_core"))
	s := strings.Split(os.Getenv("CORE_URL"), ":")
	http.ListenAndServe(":"+s[2], r)
}
