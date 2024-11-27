package tasks

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"

	"core/internal/feedback"
	"core/internal/models"
	"core/internal/story"

	"github.com/hibiken/asynq"
)

const (
	TypeStoreStories      = "store:stories"
	TypeAddScrapedUrls    = "store:scrapedurls"
	TypeStoreUserFeedback = "store:userfeedback"
)

var RedisAddr = os.Getenv("REDIS_HOSTNAME") + ":" + os.Getenv("REDIS_PORT")

func GetQueueConnection() *asynq.Client {
	return asynq.NewClient(asynq.RedisClientOpt{Addr: RedisAddr})
}

func NewStoreStoriesTask(stories []models.Story) (*asynq.Task, error) {
	payload, err := json.Marshal(stories)
	if err != nil {
		return nil, err
	}
	return asynq.NewTask(TypeStoreStories, payload), nil
}

func HandleStoreStoriesTask(ctx context.Context, t *asynq.Task) error {
	var stories []models.Story
	if err := json.Unmarshal(t.Payload(), &stories); err != nil {
		return fmt.Errorf("json.Unmarshal failed: %v: %w", err, asynq.SkipRetry)
	}
	log.Printf("Storing %d Stories", len(stories))
	story.InsertStories(stories)
	return nil
}

func NewAddScrapedUrlsTask(scrapedUrls []models.ScrapedUrl) (*asynq.Task, error) {
	payload, err := json.Marshal(scrapedUrls)
	if err != nil {
		return nil, err
	}
	return asynq.NewTask(TypeAddScrapedUrls, payload), nil
}

func HandleAddScrapedUrlsTask(ctx context.Context, t *asynq.Task) error {
	var scrapedUrls []models.ScrapedUrl
	if err := json.Unmarshal(t.Payload(), &scrapedUrls); err != nil {
		return fmt.Errorf("json.Unmarshal failed: %v: %w", err, asynq.SkipRetry)
	}
	log.Printf("Storing %d Scraped Urls", len(scrapedUrls))
	story.AddScrapedUrls(scrapedUrls)
	return nil
}

type deleteUserFeedbackPayload struct {
	UserId string
}

func NewStoreUserFeedbackTask(userFeedback feedback.UserFeedback) (*asynq.Task, error) {
	payload, err := json.Marshal(userFeedback)
	if err != nil {
		return nil, err
	}
	return asynq.NewTask(TypeStoreUserFeedback, payload), nil
}

func HandleStoreUserFeedbackTask(ctx context.Context, t *asynq.Task) error {
	var userFeedback feedback.UserFeedback
	if err := json.Unmarshal(t.Payload(), &userFeedback); err != nil {
		return fmt.Errorf("json.Unmarshal failed: %v: %w", err, asynq.SkipRetry)
	}
	log.Printf("Storing User Feedback for &s", userFeedback.UserId)
	feedback.FeedbackReceived(userFeedback)
	return nil
}
