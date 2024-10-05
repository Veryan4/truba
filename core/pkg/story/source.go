package story

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"

	"core/pkg/dbs"
	"core/pkg/models"

	"go.mongodb.org/mongo-driver/bson"
)

const sourceCollection string = "Source"

func GetSourceByName(name string) models.Source {
	mongoFilter := bson.M{"name": name}
	return dbs.GetSingle[models.Source](sourceCollection, mongoFilter)
}

func GetSourceById(sourceId string) models.Source {
	mongoFilter := bson.M{"source_id": sourceId}
	return dbs.GetSingle[models.Source](sourceCollection, mongoFilter)
}

func GetSourcesByIds(sourceIds []string) []models.Source {
	mongoFilter := bson.M{"source_id": bson.M{"$in": sourceIds}}
	return dbs.Get[models.Source](sourceCollection, mongoFilter, int64(len(sourceIds)), "", false)
}

func UpdateSourceReputation(sourceId string, reward float32) bool {
	mongoFilter := bson.M{"source_id": sourceId}
	source := dbs.GetSingle[models.Source](sourceCollection, mongoFilter)
	if source.Reputation == nil {
		source.Reputation = &reward
	} else {
		*source.Reputation += reward
	}
	return dbs.AddOrUpdateOne(sourceCollection, source) > 0
}

func GetSourceName(sourceId string) *string {
	return GetSourceById(sourceId).Name
}

func GetAllSources(language string) []models.Source {
	mongoFilter := bson.M{"language": language}
	sources := dbs.Get[models.Source](sourceCollection, mongoFilter, -1, "", false)
	if len(sources) == 0 {
		ResetSources()
		sources = dbs.Get[models.Source](sourceCollection, mongoFilter, -1, "", false)
	}
	return sources
}

func ResetSources() bool {
	apiKey := "Bearer " + os.Getenv("AIRTABLE_API_KEY")
	url := "https://api.airtable.com/v0/" + os.Getenv("AIRTABLE_ID") + "/Sources"
	client := &http.Client{}
	req, _ := http.NewRequest("GET", url, nil)
	req.Header.Add("Authorization", apiKey)
	res, err := client.Do(req)
	sources := make([]interface{}, 0)
	if err == nil {
		var airtableRecords AirTableRecords
		json.NewDecoder(res.Body).Decode(&airtableRecords)
		for _, record := range airtableRecords.Records {
			sources = append(sources, record.Fields)
		}
	} else {
		jsonFile, err := os.Open("../../data/scraper_data/sources_list.json")
		if err != nil {
			fmt.Println("Error opening sources_list.json")
			panic(err)
		}
		defer jsonFile.Close()
		byteValue, _ := io.ReadAll(jsonFile)
		var sourcesFile SourcesFile
		json.Unmarshal(byteValue, &sourcesFile)
		for _, source := range sourcesFile.Sources {
			sources = append(sources, source)
		}
	}
	defer res.Body.Close()
	return dbs.AddOrUpdateMany(sourceCollection, sources) > 0
}

type AirTableRecords struct {
	Records []AirTableFields `json:"records"`
}

type AirTableFields struct {
	Fields models.Source `json:"fields"`
}

type SourcesFile struct {
	Sources []models.Source `json:"sources"`
}
