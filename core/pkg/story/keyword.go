package story

import (
	"core/pkg/dbs"
	"core/pkg/models"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

const keywordCollection string = "Keyword"

func AddNewKeywords(keywords []models.Keyword) bool {
	allKeywordIds := map[*primitive.ObjectID]bool{}
	for _, keyword := range keywords {
		allKeywordIds[keyword.Id] = true
	}
	keywordIdList := make([]*primitive.ObjectID, 0)
	for id := range allKeywordIds {
		keywordIdList = append(keywordIdList, id)
	}
	mongoFilter := bson.M{"text": bson.M{"$in": keywordIdList}}
	currentKeywords := dbs.Get[models.Keyword](keywordCollection, mongoFilter, -1, "", false)
	allCurrentKeywordIds := map[*primitive.ObjectID]bool{}
	for _, currentKeyword := range currentKeywords {
		allCurrentKeywordIds[currentKeyword.Id] = true
	}
	newKeywords := make([]interface{}, 0)
	for _, keyword := range keywords {
		_, ok := allCurrentKeywordIds[keyword.Id]
		if !ok {
			newKeywords = append(newKeywords, keyword)
		}
	}
	insertCount := dbs.AddOrUpdateMany(keywordCollection, newKeywords)
	return insertCount > 0
}

func GetKeywordsByTexts(keywordTexts []string, language string) []models.Keyword {
	mongoFilter := bson.M{"text": bson.M{"$in": keywordTexts}, "language": language}
	return dbs.Get[models.Keyword](keywordCollection, mongoFilter, int64(len(keywordTexts)), "", false)
}
