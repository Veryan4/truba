package story

import (
	"core/internal/dbs"
	"core/internal/models"
	"core/internal/utils"

	"github.com/google/uuid"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

const authorCollection string = "Author"

func AddNewAuthors(authors []models.Author) bool {
	allAuthorIds := map[*primitive.ObjectID]bool{}
	for _, author := range authors {
		allAuthorIds[author.Id] = true
	}
	authorIdList := make([]*primitive.ObjectID, 0)
	for id := range allAuthorIds {
		authorIdList = append(authorIdList, id)
	}
	mongoFilter := bson.M{"author_id": bson.M{"$in": authorIdList}}
	currentAuthors := dbs.Get[models.Author](authorCollection, mongoFilter, -1, "", false)
	allCurrentAuthorIds := map[*primitive.ObjectID]bool{}
	for _, currentAuthor := range currentAuthors {
		allCurrentAuthorIds[currentAuthor.Id] = true
	}
	newAuthors := make([]interface{}, 0)
	for _, author := range authors {
		_, ok := allCurrentAuthorIds[author.Id]
		if !ok {
			newAuthors = append(newAuthors, author)
		}
	}
	insertCount := dbs.AddOrUpdateMany(authorCollection, newAuthors)
	return insertCount > 0
}

func GetAuthorByName(name string) (models.Author, error) {
	mongoFilter := bson.M{"name": name}
	return dbs.GetSingle[models.Author](authorCollection, mongoFilter)
}

func GetAuthorById(authorId string) (models.Author, error) {
	id, err := uuid.Parse(authorId)
	if err != nil {
		return models.Author{}, utils.LogError(err.Error())
	}
	mongoFilter := bson.M{"author_id": id}
	return dbs.GetSingle[models.Author](authorCollection, mongoFilter)
}

func GetAuthorsByIds(authorIds uuid.UUIDs) []models.Author {
	authorUuids := make(uuid.UUIDs, 0)
	for _, authorId := range authorIds {
		authorUuids = append(authorUuids, authorId)
	}
	mongoFilter := bson.M{"author_id": bson.M{"$in": authorUuids}}
	return dbs.Get[models.Author](authorCollection, mongoFilter, int64(len(authorUuids)), "", false)
}

func UpdateAuthorReputation(author_id uuid.UUID, reward float32) bool {
	mongoFilter := bson.M{"author_id": author_id}
	author, err := dbs.GetSingle[models.Author](authorCollection, mongoFilter)
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
