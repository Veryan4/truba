package story

import (
	"core/internal/dbs"
	"core/internal/models"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

const entityCollection string = "Entity"

func AddNewEntities(entities []models.Entity) bool {
	allEntityIds := map[*primitive.ObjectID]bool{}
	for _, entity := range entities {
		allEntityIds[entity.Id] = true
	}
	entityIdList := make([]*primitive.ObjectID, 0)
	for id := range allEntityIds {
		entityIdList = append(entityIdList, id)
	}
	mongoFilter := bson.M{"links": bson.M{"$in": entityIdList}}
	currentEntities := dbs.Get[models.Entity](entityCollection, mongoFilter, -1, "", false)
	allCurrentEntityIds := map[*primitive.ObjectID]bool{}
	for _, currentEntity := range currentEntities {
		allCurrentEntityIds[currentEntity.Id] = true
	}
	newEntities := make([]interface{}, 0)
	for _, entity := range entities {
		_, ok := allCurrentEntityIds[entity.Id]
		if !ok {
			newEntities = append(newEntities, entity)
		}
	}
	insertCount := dbs.AddOrUpdateMany(entityCollection, newEntities)
	return insertCount > 0
}

func GetEntitiesByLinks(entityLinks []string) []models.Entity {
	mongoFilter := bson.M{"links": bson.M{"$in": entityLinks}}
	return dbs.Get[models.Entity](entityCollection, mongoFilter, int64(len(entityLinks)), "", false)
}
