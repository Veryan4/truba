package feedback

import (
	"time"

	"core/internal/dbs"
	"core/internal/models"
	"core/internal/story"
	"core/internal/user"
	"core/internal/utils"

	"github.com/google/uuid"
	"go.mongodb.org/mongo-driver/bson"
)

const userFeedbackCollection = "UserFeedback"
const USER_FEEDBACK_COUNT = 200
const RANKING_DATA_FAVORITE_COUNT = 50
const FEEDBACK_RECEIVED_REWARD = 0.1
const URL_CLICKED_SCORE = 1.0
const SHARED_SCORE = 5.0
const ANGRY_SCORE = -5.0
const CRY_SCORE = -2.0
const NEUTRAL_SCORE = 0.0
const SMILE_SCORE = 2.0
const HAPPY_SCORE = 5.0

type FeedbackType string

const (
	READ    FeedbackType = "read"
	SHARED  FeedbackType = "shared"
	ANGRY   FeedbackType = "angry"
	CRY     FeedbackType = "cry"
	NEUTRAL FeedbackType = "neutral"
	SMILE   FeedbackType = "smile"
	HAPPY   FeedbackType = "happy"
)

type UserFeedback struct {
	UserId           string       `bson:"user_id,omitempty" json:"user_id,omitempty"`
	StoryId          string       `bson:"story_id,omitempty" json:"story_id,omitempty"`
	SearchTerm       string       `bson:"search_term,omitempty" json:"search_term,omitempty"`
	FeedbackDatetime time.Time    `bson:"feedback_datetime,omitempty" json:"feedback_datetime,omitempty"`
	FeedbackType     FeedbackType `bson:"feedback_type,omitempty" json:"feedback_type,omitempty"`
}

func RemoveFeedbackOfUser(userId string) int64 {
	mongoFilter := bson.M{"user_id": userId}
	return dbs.Remove(userFeedbackCollection, mongoFilter)
}

func GetFeedbackList(userId string) ([]UserFeedback, error) {
	mongoFilter := bson.M{}
	if userId != "defaultmodel" {
		mongoFilter["user_id"] = userId
	}
	var feedbacks []UserFeedback
	err := dbs.GetSorted(userFeedbackCollection,
		mongoFilter,
		&feedbacks,
		"feedback_datetime",
		true,
		USER_FEEDBACK_COUNT)
	return feedbacks, err
}

func ConvertFeedbackTypeToRelevancyRate(feedbackType FeedbackType) float32 {
	switch feedbackType {
	case READ:
		return URL_CLICKED_SCORE
	case SHARED:
		return SHARED_SCORE
	case ANGRY:
		return ANGRY_SCORE
	case CRY:
		return CRY_SCORE
	case NEUTRAL:
		return NEUTRAL_SCORE
	case SMILE:
		return SMILE_SCORE
	case HAPPY:
		return HAPPY_SCORE
	default:
		return 0
	}
}

func GetTFTrainingData(userId string) ([]models.RankingData, error) {
	dataEntryList := make([]models.RankingData, 0)
	feedbackList, err := GetFeedbackList(userId)
	if err != nil {
		return dataEntryList, err
	}
	relevancyDict := map[string]float32{}
	timeDict := map[string]time.Time{}
	for _, feedback := range feedbackList {
		relevancyRate := ConvertFeedbackTypeToRelevancyRate(feedback.FeedbackType)
		_, ok := relevancyDict[feedback.StoryId]
		if ok {
			relevancyDict[feedback.StoryId] += relevancyRate
		} else {
			relevancyDict[feedback.StoryId] = relevancyRate
		}
		_, ok2 := timeDict[feedback.StoryId]
		if ok2 {
			if feedback.FeedbackDatetime.After(timeDict[feedback.StoryId]) {
				timeDict[feedback.StoryId] = feedback.FeedbackDatetime
			}
		} else {
			timeDict[feedback.StoryId] = feedback.FeedbackDatetime
		}
	}
	for storyId, relevancyRate := range relevancyDict {
		currentStory, err := story.GetStoryById(storyId)
		if err != nil ||
			currentStory.Author == nil ||
			currentStory.Keywords == nil ||
			len(*currentStory.Keywords) == 0 ||
			currentStory.Entities == nil ||
			len(*currentStory.Entities) == 0 {
			continue
		}
		authorId := currentStory.Author.AuthorId.String()
		currentKeywords := *currentStory.Keywords
		mostFrequentKeyword := currentKeywords[0]
		for _, keyword := range currentKeywords {
			if *mostFrequentKeyword.Frequency < *keyword.Frequency {
				mostFrequentKeyword = keyword
			}
		}
		currentEntities := *currentStory.Entities
		mostFrequentEntity := currentEntities[0]
		for _, entity := range currentEntities {
			if *mostFrequentEntity.Frequency < *entity.Frequency {
				mostFrequentEntity = entity
			}
		}
		timeStamp := float64(timeDict[storyId].Unix())
		rankingData := models.RankingData{
			StoryId:             storyId,
			UserId:              &userId,
			RelevancyRate:       &relevancyRate,
			TimeStamp:           &timeStamp,
			StoryTitle:          currentStory.Title,
			SourceAlexaRank:     currentStory.Source.RankInAlexa,
			ReadCount:           currentStory.ReadCount,
			SharedCount:         currentStory.SharedCount,
			AngryCount:          currentStory.AngryCount,
			CryCount:            currentStory.CryCount,
			NeutralCount:        currentStory.NeutralCount,
			SmileCount:          currentStory.SmileCount,
			HappyCount:          currentStory.HappyCount,
			SourceId:            &currentStory.Source.SourceId,
			AuthorId:            &authorId,
			MostFrequentKeyword: mostFrequentKeyword.Keyword.Text,
			MostFrequentEntity:  mostFrequentEntity.Entity.Links,
		}

		dataEntryList = append(dataEntryList, rankingData)
	}
	return dataEntryList, nil
}

func FeedbackReceived(userFeedback UserFeedback) error {
	readStory := user.ReadStory{
		UserId:   userFeedback.UserId,
		StoryId:  userFeedback.StoryId,
		ReadTime: time.Now(),
	}
	user.AddReadStory(readStory)
	dbs.AddOrUpdateOne(userFeedbackCollection, userFeedback)
	var reward float32
	if userFeedback.FeedbackType == ANGRY {
		reward = -FEEDBACK_RECEIVED_REWARD
	}
	if userFeedback.FeedbackType == HAPPY || userFeedback.FeedbackType == SHARED {
		reward = FEEDBACK_RECEIVED_REWARD
	}
	currentStory, er := story.GetStoryById(userFeedback.StoryId)
	if er != nil {
		return utils.LogError(er)
	}
	uid, err := uuid.Parse(userFeedback.StoryId)
	if err != nil {
		return utils.LogError(err)
	}
	story.UpdateFeedbackCounts(uid, ConvertFeedbackTypeToString(userFeedback.FeedbackType))
	if reward == 0 {
		return nil
	}
	for _, keyword := range *currentStory.Keywords {
		user.UpdateFavoriteFromStory(userFeedback.UserId, *keyword.Keyword.Text, *keyword.Keyword.Text, reward, user.FAVORITE_KEYWORD_DB_COLLECTION_NAME, *currentStory.Language)
	}
	for _, entity := range *currentStory.Entities {
		user.UpdateFavoriteFromStory(userFeedback.UserId, *entity.Entity.Links, *entity.Entity.Text, reward, user.FAVORITE_ENTITY_DB_COLLECTION_NAME, *currentStory.Language)
	}
	user.UpdateFavoriteFromStory(userFeedback.UserId, currentStory.Source.SourceId, *currentStory.Source.Name, reward, user.FAVORITE_SOURCE_DB_COLLECTION_NAME, *currentStory.Language)
	story.UpdateSourceReputation(currentStory.Source.SourceId, reward)
	user.UpdateFavoriteFromStory(userFeedback.UserId, currentStory.Author.AuthorId.String(), *currentStory.Author.Name, reward, user.FAVORITE_AUTHOR_DB_COLLECTION_NAME, *currentStory.Language)
	story.UpdateAuthorReputation(currentStory.Author.AuthorId, reward)
	return nil
}

func ConvertFeedbackTypeToString(feedbackType FeedbackType) string {
	switch feedbackType {
	case READ:
		return "read"
	case SHARED:
		return "shared"
	case ANGRY:
		return "angry"
	case CRY:
		return "cry"
	case NEUTRAL:
		return "neutral"
	case SMILE:
		return "smile"
	case HAPPY:
		return "happy"
	default:
		return "s"
	}
}
