package main

import (
	"log"
	"net/http"
	"os"
	"strings"

	"core/internal/controllers"
	"core/internal/tasks"

	"github.com/gorilla/mux"
)

func main() {
	log.Printf("Started Core Service")
	r := mux.NewRouter()
	queueClient := tasks.GetQueueConnection()
	r = controllers.PrivateRoutes(r, queueClient)
	r.Use(controllers.LoggingMiddleware)
	log.Printf(os.Getenv("CORE_URL"))
	s := strings.Split(os.Getenv("CORE_URL"), ":")
	http.ListenAndServe(":"+s[2], r)
}
