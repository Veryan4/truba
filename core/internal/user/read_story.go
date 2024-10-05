package user

import (
	"time"

	"core/internal/dbs"

	"github.com/google/uuid"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

const readStoryCollection string = "ReadStory"
const DAYS_OF_READ_STORIES = 1

type ReadStory struct {
	UserId   string    `bson:"user_id,omitempty" json:"user_id,omitempty"`
	StoryId  string    `bson:"story_id,omitempty" json:"story_id,omitempty"`
	ReadTime time.Time `bson:"read_time,omitempty" json:"read_time,omitempty"`
}

func AddReadStory(readStory ReadStory) bool {
	return dbs.AddOrUpdateOne(readStoryCollection, readStory) > 0
}

func GetReadStoryIds(userId string) []uuid.UUID {
	mongoFilter := bson.M{
		"user_id": userId,
		"published_at": bson.M{
			"$gte": primitive.NewDateTimeFromTime(time.Now().AddDate(0, 0, -DAYS_OF_READ_STORIES)),
			"$lt":  primitive.NewDateTimeFromTime(time.Now()),
		},
	}
	readStories := dbs.Get[ReadStory](readStoryCollection, mongoFilter, -1, "", false)
	storyIds := make([]uuid.UUID, len(readStories))
	for id, readStory := range readStories {
		uid, err := uuid.Parse(readStory.StoryId)
		if err != nil {
			panic(err)
		}
		storyIds[id] = uid
	}
	return storyIds
}
