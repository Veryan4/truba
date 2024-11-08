package story

import (
	"encoding/json"
	"log"
	"net/http"
	"os"

	"core/data"
	"core/internal/dbs"
	"core/internal/models"
	"core/internal/utils"

	"go.mongodb.org/mongo-driver/bson"
)

const sourceCollection string = "Source"

func GetSourceByName(name string) (models.Source, error) {
	mongoFilter := bson.M{"name": name}
	var source models.Source
	err := dbs.GetSingle(sourceCollection, mongoFilter, &source)
	return source, err
}

func GetSourceById(sourceId string) (models.Source, error) {
	mongoFilter := bson.M{"source_id": sourceId}
	var source models.Source
	err := dbs.GetSingle(sourceCollection, mongoFilter, &source)
	return source, err
}

func GetSourcesByIds(sourceIds []string) ([]models.Source, error) {
	mongoFilter := bson.M{"source_id": bson.M{"$in": sourceIds}}
	var sources []models.Source
	err := dbs.GetSorted(sourceCollection, mongoFilter, &sources, "", false, int64(len(sourceIds)))
	return sources, err
}

func UpdateSourceReputation(sourceId string, reward float32) error {
	mongoFilter := bson.M{"source_id": sourceId}
	var source models.Source
	err := dbs.GetSingle(sourceCollection, mongoFilter, &source)
	if err != nil {
		return utils.LogError(err)
	}
	if source.Reputation == nil {
		source.Reputation = &reward
	} else {
		*source.Reputation += reward
	}
	return dbs.AddOrUpdateOne(sourceCollection, source)
}

func GetSourceName(sourceId string) (*string, error) {
	source, err := GetSourceById(sourceId)
	return source.Name, err
}

func GetAllSources(language string) ([]models.Source, error) {
	mongoFilter := bson.M{"language": language}
	var sources []models.Source
	err := dbs.GetMany(sourceCollection, mongoFilter, &sources)
	if len(sources) == 0 {
		ResetSources()
		err = dbs.GetMany(sourceCollection, mongoFilter, &sources)
	}
	return sources, err
}

func ResetSources() bool {
	dbs.Remove(sourceCollection, bson.M{})
	apiKey := "Bearer " + os.Getenv("AIRTABLE_API_KEY")
	url := "https://api.airtable.com/v0/" + os.Getenv("AIRTABLE_ID") + "/Sources"
	client := &http.Client{}
	req, _ := http.NewRequest("GET", url, nil)
	req.Header.Add("Authorization", apiKey)
	res, err := client.Do(req)
	sources := make([]interface{}, 0)
	if err == nil {
		defer res.Body.Close()
		var airtableRecords AirTableRecords
		json.NewDecoder(res.Body).Decode(&airtableRecords)
		for _, record := range airtableRecords.Records {
			sources = append(sources, record.Fields)
		}
	} else {
		jsonFile, err := data.ScraperData.ReadFile("scraper_data/sources_list.json")
		if err != nil {
			log.Println("Error opening sources_list.json")
			log.Println(err.Error())
			return false
		}
		var sourcesFile SourcesFile
		json.Unmarshal(jsonFile, &sourcesFile)
		for _, source := range sourcesFile.Sources {
			sources = append(sources, source)
		}
	}
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
