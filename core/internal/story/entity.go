package story

import (
	"log"

	"core/internal/dbs"
	"core/internal/models"

	"go.mongodb.org/mongo-driver/bson"
)

const entityCollection string = "Entity"

func AddNewEntities(entities []models.Entity) bool {
	allEntityByLinks := map[string]models.Entity{}
	for _, entity := range entities {
		allEntityByLinks[*entity.Links] = entity
	}
	entityLinksList := make([]string, 0)
	for link := range allEntityByLinks {
		entityLinksList = append(entityLinksList, link)
	}
	mongoFilter := bson.M{"links": bson.M{"$in": entityLinksList}}
	var currentEntities []models.Entity
	err := dbs.GetMany(entityCollection, mongoFilter, &currentEntities)
	if err != nil {
		log.Println(err.Error())
		return false
	}
	allCurrentEntityLinks := map[string]bool{}
	for _, currentEntity := range currentEntities {
		allCurrentEntityLinks[*currentEntity.Links] = true
	}
	newEntities := make([]interface{}, 0)
	for link, entity := range allEntityByLinks {
		_, ok := allCurrentEntityLinks[link]
		if !ok {
			newEntities = append(newEntities, entity)
		}
	}
	insertCount := dbs.AddOrUpdateMany(entityCollection, newEntities)
	return insertCount > 0
}

func GetEntitiesByLinks(entityLinks []string) ([]models.Entity, error) {
	mongoFilter := bson.M{"links": bson.M{"$in": entityLinks}}
	var entities []models.Entity
	err := dbs.GetSorted(entityCollection, mongoFilter, &entities, "", false, int64(len(entityLinks)))
	return entities, err
}
