package story

import (
	"encoding/json"
	"errors"
	"log"
	"net/http"
	"os"
	"slices"
	"sync"
	"time"

	"core/internal/dbs"
	"core/internal/models"
	"core/internal/user"
	"core/internal/utils"

	"github.com/google/uuid"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

const storyCollection string = "Story"
const STORY_DAYS_TO_EXPIRY = 90
const PREVIOUS_DAYS_OF_NEWS = 1
const RANKING_DATA_FAVORITE_COUNT = 50

func InsertStories(stories []models.Story) {
	if len(stories) == 0 {
		log.Printf("No stories to insert")
		return
	}
	authors := make([]models.Author, 0)
	keywords := make([]models.Keyword, 0)
	entities := make([]models.Entity, 0)
	for _, story := range stories {
		authors = append(authors, *story.Author)
		for _, keyword := range *story.Keywords {
			keywords = append(keywords, *keyword.Keyword)
		}
		for _, entity := range *story.Entities {
			entities = append(entities, *entity.Entity)
		}
	}
	AddNewAuthors(authors)
	AddNewKeywords(*stories[0].Language, keywords)
	AddNewEntities(entities)
	AddOrUpdateStories(stories)
	RemoveOldStories()
}

func RemoveOldStories() int64 {
	mongoFilter := bson.M{
		"published_at": bson.M{
			"$lte": primitive.NewDateTimeFromTime(time.Now().AddDate(0, 0, -STORY_DAYS_TO_EXPIRY)),
		},
	}
	return dbs.Remove(storyCollection, mongoFilter)
}

func AddOrUpdateStories(stories []models.Story) bool {
	storyInterfaces := make([]interface{}, len(stories))
	for storyIdx, story := range stories {
		storyKeywords := make([]models.KeywordInStoryDB, len(*story.Keywords))
		for i, keyword := range *story.Keywords {
			storyKeywords[i] = models.KeywordInStoryDB{
				Frequency: keyword.Frequency,
				Text:      keyword.Keyword.Text,
			}
		}
		storyEntities := make([]models.EntityInStoryDB, len(*story.Entities))
		for i, entity := range *story.Entities {
			storyEntities[i] = models.EntityInStoryDB{
				Frequency: entity.Frequency,
				Links:     entity.Entity.Links,
			}
		}
		storyinDB := models.StoryInDb{
			Id:           story.Id,
			AngryCount:   story.AngryCount,
			AuthorId:     &story.Author.AuthorId,
			Body:         story.Body,
			CryCount:     story.CryCount,
			Entities:     &storyEntities,
			HappyCount:   story.HappyCount,
			Images:       story.Images,
			Keywords:     &storyKeywords,
			Language:     story.Language,
			NeutralCount: story.NeutralCount,
			PublishedAt:  story.PublishedAt,
			ReadCount:    story.ReadCount,
			SharedCount:  story.SharedCount,
			SmileCount:   story.SmileCount,
			SourceId:     &story.Source.SourceId,
			StoryId:      story.StoryId,
			Summary:      story.Summary,
			Title:        story.Title,
			Url:          story.Url,
		}
		storyInterfaces[storyIdx] = storyinDB
	}
	return dbs.AddOrUpdateMany(storyCollection, storyInterfaces) > 0
}

func GetStoryById(storyId string) (models.Story, error) {
	id, err := uuid.Parse(storyId)
	if err != nil {
		return models.Story{}, utils.LogError(err)
	}
	mongoFilter := bson.M{"story_id": id}
	var currentStory []models.StoryInDb
	er := dbs.GetMany(storyCollection, mongoFilter, &currentStory)
	if er != nil || len(currentStory) == 0 {
		return models.Story{}, utils.LogError(er)
	}
	return BuildStoriesFromDB(currentStory)[0], nil
}

func BuildStoriesFromDB(storiesInDb []models.StoryInDb) []models.Story {
	stories := make([]models.Story, 0)
	if len(storiesInDb) == 0 {
		return stories
	}
	authors, sources, keywords, entities := GetStoryDependencies(storiesInDb)
	for _, storyInDb := range storiesInDb {
		authorIdx := slices.IndexFunc(authors, func(x models.Author) bool { return x.AuthorId == *storyInDb.AuthorId })
		sourceIdx := slices.IndexFunc(sources, func(x models.Source) bool { return x.SourceId == *storyInDb.SourceId })
		if authorIdx < 0 || sourceIdx < 0 {
			continue
		}
		storyKeywords := make([]models.KeywordInStory, 0)
		for _, keyword := range *storyInDb.Keywords {
			keywordIdx := slices.IndexFunc(keywords, func(x models.Keyword) bool { return *x.Text == *keyword.Text })
			if keywordIdx > 0 {
				storyKeywords = append(storyKeywords, models.KeywordInStory{
					Keyword:   &keywords[keywordIdx],
					Frequency: keyword.Frequency,
				})
			}
		}
		storyEntities := make([]models.EntityInStory, 0)
		for _, entity := range *storyInDb.Entities {
			entityIdx := slices.IndexFunc(entities, func(x models.Entity) bool { return *x.Links == *entity.Links })
			if entityIdx > 0 {
				storyEntities = append(storyEntities, models.EntityInStory{
					Entity:    &entities[entityIdx],
					Frequency: entity.Frequency,
				})
			}
		}
		stories = append(stories, models.Story{
			Id:           storyInDb.Id,
			AngryCount:   storyInDb.AngryCount,
			Author:       &authors[authorIdx],
			Body:         storyInDb.Body,
			CryCount:     storyInDb.CryCount,
			Entities:     &storyEntities,
			HappyCount:   storyInDb.HappyCount,
			Images:       storyInDb.Images,
			Keywords:     &storyKeywords,
			Language:     storyInDb.Language,
			NeutralCount: storyInDb.NeutralCount,
			PublishedAt:  storyInDb.PublishedAt,
			ReadCount:    storyInDb.ReadCount,
			SharedCount:  storyInDb.SharedCount,
			SmileCount:   storyInDb.SmileCount,
			Source:       &sources[sourceIdx],
			StoryId:      storyInDb.StoryId,
			Summary:      storyInDb.Summary,
			Title:        storyInDb.Title,
			Url:          storyInDb.Url,
		})
	}
	return stories
}

func BuildShortStoriesFromDB(storiesInDb []models.StoryInDb) []*models.ShortStory {
	stories := make([]*models.ShortStory, len(storiesInDb))
	if len(storiesInDb) == 0 {
		return stories
	}
	authors, sources, keywords, entities := GetStoryDependencies(storiesInDb)
	var waitGroup sync.WaitGroup
	for i, storyInDb := range storiesInDb {
		waitGroup.Add(1)
		go func() {
			defer waitGroup.Done()
			sourceIdx := slices.IndexFunc(sources, func(x models.Source) bool { return x.SourceId == *storyInDb.SourceId })
			authorIdx := slices.IndexFunc(authors, func(x models.Author) bool { return x.AuthorId == *storyInDb.AuthorId })
			if sourceIdx < 0 || authorIdx < 0 {
				return
			}
			storyKeywords := make([]string, 0)
			for _, keyword := range *storyInDb.Keywords {
				keywordIdx := slices.IndexFunc(keywords, func(x models.Keyword) bool { return *x.Text == *keyword.Text })
				if keywordIdx > 0 {
					storyKeywords = append(storyKeywords, *keywords[keywordIdx].Text)
				}
			}
			storyEntities := make([]string, 0)
			storyLinks := make([]string, 0)
			for _, entity := range *storyInDb.Entities {
				entityIdx := slices.IndexFunc(entities, func(x models.Entity) bool { return *x.Links == *entity.Links })
				if entityIdx > 0 {
					storyEntities = append(storyEntities, *entities[entityIdx].Text)
					storyLinks = append(storyLinks, *entities[entityIdx].Links)
				}
			}
			sourceId := sources[sourceIdx].SourceId
			imageString := ""
			images := *storyInDb.Images
			if len(images) > 0 {
				imageString = images[0]
			}
			authorId := authors[authorIdx].AuthorId.String()
			stories[i] = &models.ShortStory{
				Author:      authors[authorIdx].Name,
				AuthorId:    &authorId,
				Entities:    &storyEntities,
				EntityLinks: &storyLinks,
				Keywords:    &storyKeywords,
				Image:       &imageString,
				Language:    storyInDb.Language,
				PublishedAt: storyInDb.PublishedAt,
				Source:      sources[sourceIdx].Name,
				SourceId:    &sourceId,
				StoryId:     storyInDb.StoryId.String(),
				Summary:     storyInDb.Summary,
				Title:       *storyInDb.Title,
				Url:         *storyInDb.Url,
			}
		}()
		waitGroup.Wait()
	}
	return slices.DeleteFunc(
		stories,
		func(thing *models.ShortStory) bool {
			return thing == nil
		},
	)
}

func GetStoryDependencies(storiesInDb []models.StoryInDb) ([]models.Author, []models.Source, []models.Keyword, []models.Entity) {
	authorIdSet := map[uuid.UUID]bool{}
	authorIds := make([]uuid.UUID, 0)
	sourceIdSet := map[string]bool{}
	sourceIds := make([]string, 0)
	keywordSet := map[string]bool{}
	keywordTexts := make([]string, 0)
	entitySet := map[string]bool{}
	entityLinks := make([]string, 0)
	for _, storyInDb := range storiesInDb {
		_, ok := authorIdSet[*storyInDb.AuthorId]
		if !ok {
			authorIds = append(authorIds, *storyInDb.AuthorId)
			authorIdSet[*storyInDb.AuthorId] = true
		}
		_, ok2 := sourceIdSet[*storyInDb.SourceId]
		if !ok2 {
			sourceIds = append(sourceIds, *storyInDb.SourceId)
			sourceIdSet[*storyInDb.SourceId] = true
		}
		for _, keyword := range *storyInDb.Keywords {
			_, ok3 := keywordSet[*keyword.Text]
			if !ok3 {
				keywordTexts = append(keywordTexts, *keyword.Text)
				keywordSet[*keyword.Text] = true
			}
		}
		for _, entity := range *storyInDb.Entities {
			_, ok4 := entitySet[*entity.Links]
			if !ok4 {
				entityLinks = append(entityLinks, *entity.Links)
				entitySet[*entity.Links] = true
			}
		}
	}

	var authors []models.Author
	var sources []models.Source
	var keywords []models.Keyword
	var entities []models.Entity
	var waitGroup sync.WaitGroup
	waitGroup.Add(4)
	go func() {
		defer waitGroup.Done()
		a, _ := GetAuthorsByIds(authorIds)
		authors = a
	}()
	go func() {
		defer waitGroup.Done()
		s, _ := GetSourcesByIds(sourceIds)
		sources = s
	}()
	go func() {
		defer waitGroup.Done()
		k, _ := GetKeywordsByTexts(keywordTexts, *storiesInDb[0].Language)
		keywords = k
	}()
	go func() {
		defer waitGroup.Done()
		ent, _ := GetEntitiesByLinks(entityLinks)
		entities = ent
	}()
	waitGroup.Wait()
	return authors, sources, keywords, entities
}

func UpdateFeedbackCounts(storyId uuid.UUID, feedbackType string) error {
	mongoFilter := bson.M{"story_id": storyId}
	var story models.StoryInDb
	err := dbs.GetSingle(storyCollection, mongoFilter, &story)
	if err != nil {
		return utils.LogError(err)
	}
	switch feedbackType {
	case "angry":
		*story.AngryCount += 1
	case "cry":
		*story.CryCount += 1
	case "happy":
		*story.HappyCount += 1
	case "neutral":
		*story.NeutralCount += 1
	case "smile":
		*story.SmileCount += 1
	default:
		return utils.LogError(errors.New("can't find feedback type"))
	}
	return dbs.AddOrUpdateOne(authorCollection, story)
}

func GetPublicStories(language string) ([]*models.ShortStory, error) {
	if language == "" {
		language = "en"
	}
	mongoFilter := bson.M{
		"language": language,
		"published_at": bson.M{
			"$gte": primitive.NewDateTimeFromTime(time.Now().AddDate(0, 0, -PREVIOUS_DAYS_OF_NEWS)),
			"$lt":  primitive.NewDateTimeFromTime(time.Now()),
		},
	}
	var stories []models.StoryInDb
	err := dbs.GetGrouped(storyCollection, mongoFilter, &stories, "source_id", -1, "", false)
	if err != nil {
		return []*models.ShortStory{}, err
	}
	return BuildShortStoriesFromDB(stories), nil
}

func GetSingleStory(not_id_list []uuid.UUID, sourceId string, language string) (*models.ShortStory, error) {
	if language == "" {
		language = "en"
	}
	mongoFilter := bson.M{
		"language":  language,
		"source_id": sourceId,
		"published_at": bson.M{
			"$gte": primitive.NewDateTimeFromTime(time.Now().AddDate(0, 0, -PREVIOUS_DAYS_OF_NEWS)),
			"$lt":  primitive.NewDateTimeFromTime(time.Now()),
		},
		"story_id": bson.M{"$nin": not_id_list},
	}
	var stories []models.StoryInDb
	err := dbs.GetMany(storyCollection, mongoFilter, &stories)
	if err != nil || len(stories) == 0 {
		return nil, utils.LogError(err)
	}
	return BuildShortStoriesFromDB(stories)[0], nil
}

func GetRecommendedStories(userId string, language string) ([]*models.ShortStory, error) {
	if language == "" {
		language = "en"
	}
	if userId == "" {
		return GetPublicStories(language)
	}
	mongoFilter := bson.M{
		"language": language,
	}
	readStoryIds, e := user.GetReadStoryIds(userId)
	if e == nil && len(readStoryIds) > 0 {
		mongoFilter["story_id"] = bson.M{"$nin": readStoryIds}
	}
	resp, err := http.Get(os.Getenv("ML_URL") +
		"/recommendations/" + userId + "/" + language)
	if err == nil && resp.StatusCode != 404 {
		defer resp.Body.Close()
		var storyIds []uuid.UUID
		json.NewDecoder(resp.Body).Decode(&storyIds)
		isIds := make([]uuid.UUID, len(storyIds))
		isIds = append(isIds, storyIds...)
		_, ok := mongoFilter["story_id"]
		if ok {
			mongoFilter["story_id"].(bson.M)["$in"] = isIds
		} else {
			mongoFilter["story_id"] = bson.M{"$in": isIds}
		}
		var stories []models.StoryInDb
		err := dbs.GetSorted(storyCollection, mongoFilter, &stories, "", false, 12)
		if err != nil {
			return []*models.ShortStory{}, err
		}
		return BuildShortStoriesFromDB(stories), nil
	}
	mongoFilter["published_at"] = bson.M{
		"$gte": primitive.NewDateTimeFromTime(time.Now().AddDate(0, 0, -PREVIOUS_DAYS_OF_NEWS)),
		"$lt":  primitive.NewDateTimeFromTime(time.Now()),
	}
	var stories []models.StoryInDb
	er := dbs.GetGrouped(storyCollection, mongoFilter, &stories, "source_id", -1, "", false)
	if er != nil {
		return []*models.ShortStory{}, er
	}
	return BuildShortStoriesFromDB(stories), nil
}

func UpdateTFIndex(language string) ([]models.RankingData, error) {
	mongoFilter := bson.M{
		"language": language,
		"published_at": bson.M{
			"$gte": primitive.NewDateTimeFromTime(time.Now().AddDate(0, 0, -PREVIOUS_DAYS_OF_NEWS)),
			"$lt":  primitive.NewDateTimeFromTime(time.Now()),
		},
	}
	var storiesInDb []models.StoryInDb
	err := dbs.GetMany(storyCollection, mongoFilter, &storiesInDb)
	if err != nil {
		return []models.RankingData{}, err
	}
	stories := BuildStoriesFromDB(storiesInDb)
	rankingData := make([]models.RankingData, 0)
	for _, story := range stories {
		if *story.Keywords == nil || len(*story.Keywords) == 0 || *story.Entities == nil || len(*story.Entities) == 0 {
			continue
		}
		keywords := *story.Keywords
		mostFrequentKeyword := keywords[0]
		for _, keyword := range *story.Keywords {
			if *mostFrequentKeyword.Frequency > *keyword.Frequency {
				mostFrequentKeyword = keyword
			}
		}
		entities := *story.Entities
		mostFrequentEntity := entities[0]
		for _, entity := range *story.Entities {
			if *mostFrequentEntity.Frequency > *entity.Frequency {
				mostFrequentEntity = entity
			}
		}
		authorIdString := story.Author.AuthorId.String()
		rankingData = append(rankingData, models.RankingData{
			StoryId:             story.StoryId.String(),
			StoryTitle:          story.Title,
			SourceAlexaRank:     story.Source.RankInAlexa,
			ReadCount:           story.ReadCount,
			SharedCount:         story.SharedCount,
			AngryCount:          story.AngryCount,
			CryCount:            story.CryCount,
			NeutralCount:        story.NeutralCount,
			SmileCount:          story.SmileCount,
			HappyCount:          story.HappyCount,
			SourceId:            &story.Source.SourceId,
			AuthorId:            &authorIdString,
			MostFrequentKeyword: mostFrequentKeyword.Keyword.Text,
			MostFrequentEntity:  mostFrequentEntity.Entity.Links,
		})
	}
	return rankingData, nil
}
