package story

import (
	"log"

	"core/internal/dbs"
	"core/internal/models"

	"go.mongodb.org/mongo-driver/bson"
)

const keywordCollection string = "Keyword"

func AddNewKeywords(language string, keywords []models.Keyword) bool {
	allKeywordTexts := map[string]models.Keyword{}
	for _, keyword := range keywords {
		allKeywordTexts[*keyword.Text] = keyword
	}
	keywordIdList := make([]string, 0)
	for text := range allKeywordTexts {
		keywordIdList = append(keywordIdList, text)
	}
	mongoFilter := bson.M{"language": language, "text": bson.M{"$in": keywordIdList}}
	var currentKeywords []models.Keyword
	err := dbs.GetMany(keywordCollection, mongoFilter, &currentKeywords)
	if err != nil {
		log.Println(err.Error())
		return false
	}
	allCurrentKeywordTexts := map[string]bool{}
	for _, currentKeyword := range currentKeywords {
		allCurrentKeywordTexts[*currentKeyword.Text] = true
	}
	newKeywords := make([]interface{}, 0)
	for text, keyword := range allKeywordTexts {
		_, ok := allCurrentKeywordTexts[text]
		if !ok {
			newKeywords = append(newKeywords, keyword)
		}
	}
	insertCount := dbs.AddOrUpdateMany(keywordCollection, newKeywords)
	return insertCount > 0
}

func GetKeywordsByTexts(keywordTexts []string, language string) ([]models.Keyword, error) {
	mongoFilter := bson.M{"text": bson.M{"$in": keywordTexts}, "language": language}
	var keywords []models.Keyword
	err := dbs.GetSorted(keywordCollection, mongoFilter, &keywords, "", false, int64(len(keywordTexts)))
	return keywords, err
}
