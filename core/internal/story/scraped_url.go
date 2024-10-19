package story

import (
	"time"

	"core/internal/dbs"
	"core/internal/models"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

const scrapedUrlCollection string = "ScrapedUrl"
const DAYS_OF_PREVIOUSLY_SCRAPED = 3

func AddScrapedUrls(scrapedUrls []models.ScrapedUrl) bool {
	scrapedInterfaces := make([]interface{}, 0)
	for _, scrapedUrl := range scrapedUrls {
		scrapedInterfaces = append(scrapedInterfaces, scrapedUrl)
	}
	return dbs.AddOrUpdateMany(scrapedUrlCollection, scrapedInterfaces) > 0
}

func GetScrapedUrlsBySourceName(sourceName string) ([]models.ScrapedUrl, error) {
	mongoFilter := bson.M{
		"source_name": sourceName,
		"published_at": bson.M{
			"$gte": primitive.NewDateTimeFromTime(time.Now().AddDate(0, 0, -DAYS_OF_PREVIOUSLY_SCRAPED)),
			"$lt":  primitive.NewDateTimeFromTime(time.Now()),
		},
	}
	var scrapedUrl []models.ScrapedUrl
	err := dbs.GetMany(scrapedUrlCollection, mongoFilter, &scrapedUrl)
	return scrapedUrl, err
}
