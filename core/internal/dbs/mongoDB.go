package dbs

import (
	"context"
	"fmt"
	"log"
	"os"
	"reflect"

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
	var result bson.M
	if err := client.Database(dbName).RunCommand(context.TODO(), bson.D{{"ping", 1}}).Decode(&result); err != nil {
		panic(err)
	}
	log.Println("Pinged your deployment. You successfully connected to MongoDB!")

	return client.Database(dbName)
}

func GetMany(collection string,
	filter interface{},
	value interface{}) error {
	col := myDb.Collection(collection)
	results, err := col.Find(context.TODO(), filter)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			log.Printf("No documents for in %s\n", collection)
			setNilToEmptySlice(value)
			return nil
		}
		return err
	}
	if err := results.All(context.TODO(), value); err != nil {
		log.Printf("Error marshalling list for %s\n", collection)
		return err
	}
	setNilToEmptySlice(value)
	return nil
}

func GetSorted(collection string,
	filter interface{},
	value interface{},
	sort string,
	reverse bool,
	limit int64) error {
	col := myDb.Collection(collection)
	findOptions := options.Find()
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
		if err == mongo.ErrNoDocuments {
			log.Printf("No documents for in %s\n", collection)
			setNilToEmptySlice(value)
			return nil
		}
		return err
	}
	if err := results.All(context.TODO(), value); err != nil {
		log.Printf("Error marshalling list for %s\n", collection)
		return err
	}
	setNilToEmptySlice(value)
	return nil
}

func GetSingle(collection string, filter interface{}, value interface{}) error {
	col := myDb.Collection(collection)
	err := col.FindOne(context.TODO(), filter).Decode(value)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			log.Printf("No single document found for %s\n", collection)
		}
		return err
	}
	return nil
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

func GetGrouped(collection string,
	filter interface{},
	value interface{},
	groupBy string,
	limit int64,
	sort string,
	reverse bool) error {
	col := myDb.Collection(collection)
	aggregate := mongo.Pipeline{
		bson.D{{"$match", filter}},
		bson.D{{"$group", bson.D{{"_id", "$" + groupBy}, {"doc", bson.M{"$first": "$$ROOT"}}}}},
	}
	if sort != "" {
		var sortDirection int8 = 1
		if reverse {
			sortDirection = -1
		}
		aggregate = append(aggregate, bson.D{{"$sort", bson.M{sort: sortDirection}}})
	}
	if limit > 0 {
		aggregate = append(aggregate, bson.D{{"$limit", limit}})
	}
	aggregate = append(aggregate, bson.D{{"$replaceRoot", bson.M{"newRoot": "$doc"}}})
	results, err := col.Aggregate(context.TODO(), aggregate)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			log.Printf("No documents for in %s\n", collection)
			setNilToEmptySlice(value)
			return nil
		}
		return err
	}
	if err := results.All(context.TODO(), value); err != nil {
		log.Printf("Error marshalling list for %s\n", collection)
		return err
	}
	setNilToEmptySlice(value)
	return nil
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

func setNilToEmptySlice(value interface{}) {
	reflected := reflect.ValueOf(value)
	if reflected.Elem().IsNil() {
		elemSlice := reflect.MakeSlice(reflect.SliceOf(reflected.Elem().Type().Elem()), 0, 0)
		reflected.Elem().Set(elemSlice)
	}
}
