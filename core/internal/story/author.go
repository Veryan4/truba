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
	allAuthorsById := map[uuid.UUID]models.Author{}
	for _, author := range authors {
		allAuthorsById[author.AuthorId] = author
	}
	authorIdList := make([]uuid.UUID, 0)
	for id := range allAuthorsById {
		authorIdList = append(authorIdList, id)
	}
	mongoFilter := bson.M{"author_id": bson.M{"$in": authorIdList}}
	var currentAuthors []models.Author
	err := dbs.GetMany(authorCollection, mongoFilter, &currentAuthors)
	if err != nil {
		log.Println("failed to fetch current authors")
		return false
	}
	allCurrentAuthorIds := map[uuid.UUID]bool{}
	for _, currentAuthor := range currentAuthors {
		allCurrentAuthorIds[currentAuthor.AuthorId] = true
	}
	newAuthors := make([]interface{}, 0)
	for id, author := range allAuthorsById {
		_, ok := allCurrentAuthorIds[id]
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
		return models.Author{}, utils.LogError(err)
	}
	mongoFilter := bson.M{"author_id": id}
	var author models.Author
	er := dbs.GetSingle(authorCollection, mongoFilter, &author)
	return author, er
}

func GetAuthorsByIds(authorIds []uuid.UUID) ([]models.Author, error) {
	mongoFilter := bson.M{"author_id": bson.M{"$in": authorIds}}
	var authors []models.Author
	err := dbs.GetSorted(authorCollection, mongoFilter, &authors, "", false, int64(len(authorIds)))
	return authors, err

}

func UpdateAuthorReputation(author_id uuid.UUID, reward float32) error {
	mongoFilter := bson.M{"author_id": author_id}
	var author models.Author
	err := dbs.GetSingle(authorCollection, mongoFilter, &author)
	if err != nil {
		return utils.LogError(err)
	}
	if author.Reputation == nil {
		author.Reputation = &reward
	} else {
		*author.Reputation += reward
	}
	return dbs.AddOrUpdateOne(authorCollection, author)
}
