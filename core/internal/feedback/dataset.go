package feedback

import (
	"time"

	"core/internal/models"
	"core/internal/story"
	"core/internal/user"

	"github.com/google/uuid"
)

func GetTrainingDataSet() ([]models.RankingData, error) {
	dataEntryList := make([]models.RankingData, 0)
	feedbackList, err := GetFeedbackList()
	if err != nil {
		return dataEntryList, err
	}
	relevancyDict := map[string]float32{}
	timeDict := map[string]time.Time{}
	userById := map[string]int64{}
	for _, feedback := range feedbackList {
		_, ok := userById[feedback.UserId]
		if !ok {
			uid, err := uuid.Parse(feedback.UserId)
			if err != nil {
				continue
			}
			currentUser, err2 := user.GetUserById(uid)
			if err2 != nil {
				continue
			}
			userById[feedback.UserId] = currentUser.Id.Timestamp().Unix()
		}
		relevancyRate := ConvertFeedbackTypeToRelevancyRate(feedback.FeedbackType)
		_, ok2 := relevancyDict[feedback.StoryId]
		if ok2 {
			relevancyDict[feedback.StoryId] += relevancyRate
		} else {
			relevancyDict[feedback.StoryId] = relevancyRate
		}
		_, ok3 := timeDict[feedback.StoryId]
		if ok3 {
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
		timeStamp := timeDict[storyId].Unix()
		currentUserId := userById[feedback.UserId]
		authorId := currentStory.Author.Id.Timestamp().Unix()
		sourceId := currentStory.Source.Id.Timestamp().Unix()
		mostFrequentKeywordId := mostFrequentKeyword.Keyword.Id.Timestamp().Unix()
		mostFrequentEntityId := mostFrequentEntity.Entity.Id.Timestamp().Unix()
		rankingData := models.RankingData{
			StoryId:             currentStory.Id.Timestamp().Unix(),
			UserId:              &currentUserId,
			RelevancyRate:       &relevancyRate,
			TimeStamp:           &timeStamp,
			SourceAlexaRank:     currentStory.Source.RankInAlexa,
			ReadCount:           currentStory.ReadCount,
			SharedCount:         currentStory.SharedCount,
			AngryCount:          currentStory.AngryCount,
			CryCount:            currentStory.CryCount,
			NeutralCount:        currentStory.NeutralCount,
			SmileCount:          currentStory.SmileCount,
			HappyCount:          currentStory.HappyCount,
			SourceId:            &sourceId,
			AuthorId:            &authorId,
			MostFrequentKeyword: &mostFrequentKeywordId,
			MostFrequentEntity:  &mostFrequentEntityId,
		}
		dataEntryList = append(dataEntryList, rankingData)
	}
	return dataEntryList, nil
}

func UpdateIndex(language string) ([]models.RankingData, error) {
	stories, err := story.GetPreviousDaysOfNews(language)
	if err != nil {
		return []models.RankingData{}, err
	}
	rankingData := make([]models.RankingData, 0)
	for _, currentStory := range stories {
		if *currentStory.Keywords == nil || len(*currentStory.Keywords) == 0 || *currentStory.Entities == nil || len(*currentStory.Entities) == 0 {
			continue
		}
		keywords := *currentStory.Keywords
		mostFrequentKeyword := keywords[0]
		for _, keyword := range *currentStory.Keywords {
			if *mostFrequentKeyword.Frequency > *keyword.Frequency {
				mostFrequentKeyword = keyword
			}
		}
		entities := *currentStory.Entities
		mostFrequentEntity := entities[0]
		for _, entity := range *currentStory.Entities {
			if *mostFrequentEntity.Frequency > *entity.Frequency {
				mostFrequentEntity = entity
			}
		}
		authorId := currentStory.Author.Id.Timestamp().Unix()
		sourceId := currentStory.Source.Id.Timestamp().Unix()
		mostFrequentKeywordId := mostFrequentKeyword.Keyword.Id.Timestamp().Unix()
		mostFrequentEntityId := mostFrequentEntity.Entity.Id.Timestamp().Unix()
		rankingData = append(rankingData, models.RankingData{
			StoryId:             currentStory.Id.Timestamp().Unix(),
			SourceAlexaRank:     currentStory.Source.RankInAlexa,
			ReadCount:           currentStory.ReadCount,
			SharedCount:         currentStory.SharedCount,
			AngryCount:          currentStory.AngryCount,
			CryCount:            currentStory.CryCount,
			NeutralCount:        currentStory.NeutralCount,
			SmileCount:          currentStory.SmileCount,
			HappyCount:          currentStory.HappyCount,
			SourceId:            &sourceId,
			AuthorId:            &authorId,
			MostFrequentKeyword: &mostFrequentKeywordId,
			MostFrequentEntity:  &mostFrequentEntityId,
		})
	}
	return rankingData, nil
}
