package controllers

import (
	"log"
	"net/http"

	"core/internal/feedback"
	"core/internal/models"
	"core/internal/story"
	"core/internal/tasks"
	"core/internal/user"

	"github.com/gorilla/mux"
	"github.com/hibiken/asynq"
)

func PrivateRoutes(r *mux.Router, queueClient *asynq.Client) *mux.Router {

	r.HandleFunc("/stories", func(w http.ResponseWriter, r *http.Request) {
		var stories []models.Story
		ok := DecodeJSON(w, r, &stories)
		if !ok {
			return
		}
		task, err := tasks.NewStoreStoriesTask(stories)
		if err != nil {
			RespondWithError(w, 500, "Could not create NewStoreStoriesTask")
			return
		}
		info, err := queueClient.Enqueue(task)
		if err != nil {
			RespondWithError(w, 500, "Could not enqueue NewStoreStoriesTask")
			return
		}
		log.Printf("enqueued task: id=%s queue=%s", info.ID, info.Queue)
		RespondWithJSON(w, http.StatusOK, map[string]string{"AddStoriesJob": "Job Queued"})
	}).Methods("POST")

	r.HandleFunc("/scraped", func(w http.ResponseWriter, r *http.Request) {
		sourceName := r.URL.Query().Get("source_name")
		scrapedUrls, err := story.GetScrapedUrlsBySourceName(sourceName)
		if err != nil {
			RespondWithError(w, 500, err.Error())
			return
		}
		RespondWithJSON(w, http.StatusOK, scrapedUrls)
	}).Methods("GET")

	r.HandleFunc("/scraped", func(w http.ResponseWriter, r *http.Request) {
		var scrapedUrls []models.ScrapedUrl
		ok := DecodeJSON(w, r, &scrapedUrls)
		if !ok {
			return
		}
		task, err := tasks.NewAddScrapedUrlsTask(scrapedUrls)
		if err != nil {
			RespondWithError(w, 500, "Could not create NewAddScrapedUrlsTask")
			return
		}
		info, err := queueClient.Enqueue(task)
		if err != nil {
			RespondWithError(w, 500, "Could not enqueue NewAddScrapedUrlsTask")
			return
		}
		log.Printf("enqueued task: id=%s queue=%s", info.ID, info.Queue)
		RespondWithJSON(w, http.StatusOK, map[string]string{"AddScrapedUrls": "Job Queued"})
	}).Methods("POST")

	r.HandleFunc("/sources/{language}", func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		language := vars["language"]
		sources, err := story.GetAllSources(language)
		if err != nil {
			RespondWithError(w, 500, err.Error())
			return
		}
		RespondWithJSON(w, http.StatusOK, sources)
	}).Methods("GET")

	r.HandleFunc("/sources/reset", func(w http.ResponseWriter, r *http.Request) {
		ok := story.ResetSources()
		if ok {
			RespondWithJSON(w, http.StatusOK, map[string]string{"message": "Successfully reset sources"})
			return
		}
		RespondWithError(w, http.StatusBadRequest, "Failed to reset sources")
	}).Methods("GET")

	r.HandleFunc("/authors/name", func(w http.ResponseWriter, r *http.Request) {
		authorName := r.URL.Query().Get("author_name")
		author, err := story.GetAuthorByName(authorName)
		if err != nil {
			RespondWithError(w, 404, "Author not found")
			return
		}
		RespondWithJSON(w, http.StatusOK, author)
	}).Methods("GET")

	r.HandleFunc("/training/{user_id}", func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		userId := vars["user_id"]
		data, err := feedback.GetTFTrainingData(userId)
		if err != nil {
			RespondWithError(w, 500, err.Error())
			return
		}
		if len(data) == 0 {
			RespondWithError(w, 404, "No Training Data Found")
			return
		}
		RespondWithJSON(w, http.StatusOK, data)
	}).Methods("GET")

	r.HandleFunc("/training/{user_id}", func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		userId := vars["user_id"]
		task, err := tasks.NewDeleteUserFeedbackTask(userId)
		if err != nil {
			RespondWithError(w, 500, "Could not create NewDeleteUserFeedbackTask")
			return
		}
		info, err := queueClient.Enqueue(task)
		if err != nil {
			RespondWithError(w, 500, "Could not enqueue NewDeleteUserFeedbackTask")
			return
		}
		log.Printf("enqueued task: id=%s queue=%s", info.ID, info.Queue)
		RespondWithJSON(w, http.StatusOK, map[string]string{"feedbackJob": "Job Queued"})
	}).Methods("DELETE")

	r.HandleFunc("/update-index/{language}", func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		language := vars["language"]
		data, err := story.UpdateTFIndex(language)
		if err != nil {
			RespondWithError(w, 500, err.Error())
			return
		}
		RespondWithJSON(w, http.StatusOK, data)
	}).Methods("GET")

	r.HandleFunc("/user/ids", func(w http.ResponseWriter, r *http.Request) {
		ids := user.GetUserIds()
		if len(ids) == 0 {
			RespondWithError(w, 404, "No User Ids Found")
			return
		}
		RespondWithJSON(w, http.StatusOK, ids)
	}).Methods("GET")

	r.HandleFunc("/news/{language}", func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		language := vars["language"]
		subscriptions, err := story.GetPublicStories(language)
		if err != nil {
			RespondWithError(w, 500, err.Error())
			return
		}
		RespondWithJSON(w, http.StatusOK, subscriptions)
	}).Methods("GET")

	return r
}
