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

func AddReadStory(readStory ReadStory) error {
	return dbs.AddOrUpdateOne(readStoryCollection, readStory)
}

func GetReadStoryIds(userId string) ([]uuid.UUID, error) {
	mongoFilter := bson.M{
		"user_id": userId,
		"read_time": bson.M{
			"$gte": primitive.NewDateTimeFromTime(time.Now().AddDate(0, 0, -DAYS_OF_READ_STORIES)),
			"$lt":  primitive.NewDateTimeFromTime(time.Now()),
		},
	}
	var readStories []ReadStory
	err := dbs.GetMany(readStoryCollection, mongoFilter, &readStories)
	if err != nil {
		return uuid.UUIDs{}, err
	}
	storyIds := make([]uuid.UUID, len(readStories))
	for id, readStory := range readStories {
		uid, er := uuid.Parse(readStory.StoryId)
		if er != nil {
			return uuid.UUIDs{}, er
		}
		storyIds[id] = uid
	}
	return storyIds, nil
}
