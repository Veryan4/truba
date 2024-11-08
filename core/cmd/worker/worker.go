package main

import (
	"log"

	"core/internal/tasks"

	"github.com/hibiken/asynq"
)

func main() {
	log.Printf("Started Task Worker")
	srv := asynq.NewServer(
		asynq.RedisClientOpt{Addr: tasks.RedisAddr},
		asynq.Config{
			Concurrency: 10,
			Queues: map[string]int{
				"critical": 6,
				"default":  3,
				"low":      1,
			},
		},
	)

	mux := asynq.NewServeMux()
	mux.HandleFunc(tasks.TypeStoreStories, tasks.HandleStoreStoriesTask)
	mux.HandleFunc(tasks.TypeAddScrapedUrls, tasks.HandleAddScrapedUrlsTask)
	mux.HandleFunc(tasks.TypeDeleteUserFeedback, tasks.HandleDeleteUserFeedbackTask)
	mux.HandleFunc(tasks.TypeStoreUserFeedback, tasks.HandleStoreUserFeedbackTask)

	if err := srv.Run(mux); err != nil {
		log.Fatalf("could not run worker server: %v", err)
	}
}
