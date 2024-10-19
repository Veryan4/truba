package story

import (
	"log"

	"core/internal/dbs"
	"core/internal/models"
	"core/internal/utils"

	"github.com/google/uuid"
	"go.mongodb.org/mongo-driver/bson"
)

const authorCollection string = "Author"

func AddNewAuthors(authors []models.Author) bool {
	allAuthorsByName := map[string]models.Author{}
	for _, author := range authors {
		allAuthorsByName[*author.Name] = author
	}
	authorNameList := make([]string, 0)
	for name := range allAuthorsByName {
		authorNameList = append(authorNameList, name)
	}
	mongoFilter := bson.M{"name": bson.M{"$in": authorNameList}}
	var currentAuthors []models.Author
	err := dbs.GetMany(authorCollection, mongoFilter, &currentAuthors)
	if err != nil {
		log.Println("failed to fetch current authors")
		return false
	}
	allCurrentAuthorNames := map[string]bool{}
	for _, currentAuthor := range currentAuthors {
		allCurrentAuthorNames[*currentAuthor.Name] = true
	}
	newAuthors := make([]interface{}, 0)
	for name, author := range allAuthorsByName {
		_, ok := allCurrentAuthorNames[name]
		if !ok {
			newAuthors = append(newAuthors, author)
		}
	}
	insertCount := dbs.AddOrUpdateMany(authorCollection, newAuthors)
	return insertCount > 0
}

func GetAuthorByName(name string) (models.Author, error) {
	mongoFilter := bson.M{"name": name}
	var author models.Author
	err := dbs.GetSingle(authorCollection, mongoFilter, &author)
	return author, err
}

func GetAuthorById(authorId string) (models.Author, error) {
	id, err := uuid.Parse(authorId)
	if err != nil {
		return models.Author{}, utils.LogError(err.Error())
	}
	mongoFilter := bson.M{"author_id": id}
	var author models.Author
	er := dbs.GetSingle(authorCollection, mongoFilter, &author)
	return author, er
}

func GetAuthorsByIds(authorIds uuid.UUIDs) ([]models.Author, error) {
	authorUuids := make(uuid.UUIDs, 0)
	for _, authorId := range authorIds {
		authorUuids = append(authorUuids, authorId)
	}
	mongoFilter := bson.M{"author_id": bson.M{"$in": authorUuids}}
	var authors []models.Author
	err := dbs.GetSorted(authorCollection, mongoFilter, &authors, "", false, int64(len(authorUuids)))
	return authors, err

}

func UpdateAuthorReputation(author_id uuid.UUID, reward float32) bool {
	mongoFilter := bson.M{"author_id": author_id}
	var author models.Author
	err := dbs.GetSingle(authorCollection, mongoFilter, &author)
	if err != nil {
		utils.LogError(err.Error())
		return false
	}
	if author.Reputation == nil {
		author.Reputation = &reward
	} else {
		*author.Reputation += reward
	}
	return dbs.AddOrUpdateOne(authorCollection, author) > 0
}
