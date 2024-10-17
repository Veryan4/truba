package dbs

import (
	"context"
	"fmt"
	"log"
	"os"

	"core/internal/utils"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var dbName = os.Getenv("ENVIRONMENT")
var mongoUri = "mongodb://" + os.Getenv("MONGO_USERNAME") + ":" + os.Getenv(
	"MONGO_PASSWORD") + "@" + os.Getenv(
	"CORE_DB_HOSTNAME") + ".default.svc.cluster.local:" + os.Getenv(
	"CORE_DB_PORT") + "/" + dbName + "?authSource=admin"
var myDb = dbConnection()

type MongoObjId struct {
	Id primitive.ObjectID `bson:"_id"`
}

func dbConnection() *mongo.Database {
	serverAPI := options.ServerAPI(options.ServerAPIVersion1)
	opts := options.Client().ApplyURI(mongoUri).SetServerAPIOptions(serverAPI).SetCompressors([]string{"zlib"})
	client, err := mongo.Connect(context.TODO(), opts)
	if err != nil {
		panic(err)
	}
	//defer func() {
	//	if err = client.Disconnect(context.TODO()); err != nil {
	//		panic(err)
	//	}
	//}()
	var result bson.M
	if err := client.Database(dbName).RunCommand(context.TODO(), bson.D{{"ping", 1}}).Decode(&result); err != nil {
		panic(err)
	}
	log.Println("Pinged your deployment. You successfully connected to MongoDB!")

	return client.Database(dbName)
}

func Get[T any](collection string,
	filter interface{},
	limit int64,
	sort string,
	reverse bool) []T {
	col := myDb.Collection(collection)
	var findOptions *options.FindOptions
	if limit > 0 {
		findOptions = findOptions.SetLimit(limit)
	}
	if sort != "" {
		var sortDirection int8 = 1
		if reverse {
			sortDirection = -1
		}
		findOptions = findOptions.SetSort(bson.D{{sort, sortDirection}})
	}
	results, err := col.Find(context.TODO(), filter, findOptions)
	if err != nil {
		if err != mongo.ErrNoDocuments {
			log.Printf("Error retrieving documents from %s\n", collection)
		}
		return make([]T, 0)
	}
	var list []T
	if err := results.All(context.TODO(), &list); err != nil {
		log.Printf("Error marshalling list for %s\n", collection)
		return make([]T, 0)
	}
	return list
}

func GetSingle[T any](collection string, filter interface{}) (T, error) {
	documents := Get[T](collection, filter, 1, "", false)
	if len(documents) == 0 {
		var document T
		return document, utils.LogError("Failed to retrive single document %s\n", collection)
	}
	return documents[0], nil
}

func GetDistinctValues(collection string,
	filter interface{},
	distinct string) []string {
	col := myDb.Collection(collection)
	results, err := col.Distinct(context.TODO(), distinct, filter)
	if err != nil {
		if err != mongo.ErrNoDocuments {
			fmt.Printf("Error retrieving documents from %s\n", collection)
		}
		return make([]string, 0)
	}
	strings := make([]string, len(results))
	for i, v := range results {
		strings[i] = fmt.Sprint(v)
	}
	return strings
}

func GetGrouped[T any](collection string,
	filter interface{},
	groupBy string,
	limit int64,
	sort string,
	reverse bool) []T {
	col := myDb.Collection(collection)
	aggregate := []bson.M{
		{"$match": filter},
		{"$group": bson.M{"_id": ("$" + groupBy), "items": bson.M{"$push": "$$ROOT"}}},
	}
	if sort != "" {
		var sortDirection int8 = 1
		if reverse {
			sortDirection = -1
		}
		aggregate = append(aggregate, bson.M{"$sort": bson.M{sort: sortDirection}})
	}
	if limit != 0 {
		aggregate = append(aggregate, bson.M{"$limit": limit})
	}
	results, err := col.Aggregate(context.TODO(), aggregate)
	if err != nil {
		if err != mongo.ErrNoDocuments {
			log.Printf("Error retrieving documents from %s\n", collection)
		}
		return make([]T, 0)
	}
	var list []T
	if err := results.All(context.TODO(), &list); err != nil {
		log.Printf("Error marshalling list for %s\n", collection)
		return make([]T, 0)
	}
	return list
}

func AddOrUpdateMany(collection string, documents []interface{}) int64 {
	col := myDb.Collection(collection)
	operations := []mongo.WriteModel{}
	for _, document := range documents {
		val, ok := document.(MongoObjId)
		if ok {
			update := mongo.NewUpdateOneModel().SetFilter(bson.D{{"_id", val.Id}}).SetUpdate(bson.D{{"$set", document}}).SetUpsert(true)
			operations = append(operations, update)
		} else {
			insert := mongo.NewInsertOneModel().SetDocument(document)
			operations = append(operations, insert)
		}
	}
	results, err := col.BulkWrite(context.TODO(), operations)
	if err != nil {
		log.Printf("Failed to bulk Upsert %s\n", collection)
		return 0
	}
	return results.UpsertedCount
}

func AddOrUpdateOne(collection string, document interface{}) int64 {
	documents := make([]interface{}, 0)
	documents = append(documents, document)
	return AddOrUpdateMany(collection, documents)
}

func Remove(collection string, filter interface{}) int64 {
	col := myDb.Collection(collection)
	result, err := col.DeleteMany(context.TODO(), filter)
	if err != nil {
		log.Printf("Failed to bulk Delete %s\n", collection)
		return 0
	}
	return result.DeletedCount
}
