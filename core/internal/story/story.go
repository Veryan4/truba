package story

import (
	"encoding/json"
	"errors"
	"net/http"
	"os"
	"slices"
	"time"

	"core/internal/dbs"
	"core/internal/models"
	"core/internal/user"

	"github.com/google/uuid"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

const storyCollection string = "Story"
const STORY_DAYS_TO_EXPIRY = 90
const PREVIOUS_DAYS_OF_NEWS = 1
const RANKING_DATA_FAVORITE_COUNT = 50

func InsertStories(stories []models.Story) {
	authors := make([]models.Author, 0)
	keywords := make([]models.Keyword, 0)
	entities := make([]models.Entity, 0)
	for _, story := range stories {
		authors = append(authors, *story.Author)
		for _, keyword := range keywords {
			keywords = append(keywords, keyword)
		}
		for _, entity := range entities {
			entities = append(entities, entity)
		}
	}
	AddNewAuthors(authors)
	AddNewKeywords(keywords)
	AddNewEntities(entities)
	RemoveOldStories()
	AddOrUpdateStories(stories)
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
		storyEntities := make([]models.EntityInStoryDB, len(*story.Keywords))
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
	return dbs.Remove(storyCollection, storyInterfaces) > 0
}

func GetStoryById(storyId string) (models.Story, error) {
	id, err := uuid.Parse(storyId)
	if err != nil {
		panic(err)
	}
	mongoFilter := bson.M{"story_id": id}
	currentStory := dbs.Get[models.StoryInDb](storyCollection, mongoFilter, 1, "", false)
	if len(currentStory) == 0 {
		return models.Story{}, errors.New("Couldn't find Story")
	}
	return BuildStoriesFromDB(currentStory)[0], nil
}

func BuildStoriesFromDB(storiesInDb []models.StoryInDb) []models.Story {
	stories := make([]models.Story, len(storiesInDb))
	if len(storiesInDb) == 0 {
		return stories
	}
	authors, sources, keywords, entities := GetStoryDependencies(storiesInDb)
	for storyIdx, storyInDb := range storiesInDb {
		authorIdx := slices.IndexFunc(authors, func(x models.Author) bool { return x.AuthorId == *storyInDb.AuthorId })
		sourceIdx := slices.IndexFunc(sources, func(x models.Source) bool { return x.SourceId == *storyInDb.SourceId })
		storyKeywords := make([]models.KeywordInStory, len(*storyInDb.Keywords))
		for i, keyword := range *storyInDb.Keywords {
			keywordIdx := slices.IndexFunc(keywords, func(x models.Keyword) bool { return x.Text == keyword.Text })
			storyKeywords[i] = models.KeywordInStory{
				Keyword:   &keywords[keywordIdx],
				Frequency: keyword.Frequency,
			}
		}
		storyEntities := make([]models.EntityInStory, len(*storyInDb.Entities))
		for i, entity := range *storyInDb.Entities {
			entityIdx := slices.IndexFunc(entities, func(x models.Entity) bool { return x.Links == entity.Links })
			storyEntities[i] = models.EntityInStory{
				Entity:    &entities[entityIdx],
				Frequency: entity.Frequency,
			}
		}
		stories[storyIdx] = models.Story{
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
		}
	}
	return stories
}

func BuildShortStoriesFromDB(storiesInDb []models.StoryInDb) []models.ShortStory {
	stories := make([]models.ShortStory, len(storiesInDb))
	if len(storiesInDb) == 0 {
		return stories
	}
	authors, sources, keywords, entities := GetStoryDependencies(storiesInDb)
	for storyIdx, storyInDb := range storiesInDb {
		authorIdx := slices.IndexFunc(authors, func(x models.Author) bool { return x.AuthorId == *storyInDb.AuthorId })
		sourceIdx := slices.IndexFunc(sources, func(x models.Source) bool { return x.SourceId == *storyInDb.SourceId })
		storyKeywords := make([]string, len(*storyInDb.Keywords))
		for i, keyword := range *storyInDb.Keywords {
			keywordIdx := slices.IndexFunc(keywords, func(x models.Keyword) bool { return x.Text == keyword.Text })
			storyKeywords[i] = *keywords[keywordIdx].Text
		}
		storyEntities := make([]string, len(*storyInDb.Entities))
		for i, entity := range *storyInDb.Entities {
			entityIdx := slices.IndexFunc(entities, func(x models.Entity) bool { return x.Links == entity.Links })
			storyEntities[i] = *entities[entityIdx].Text
		}
		stories[storyIdx] = models.ShortStory{
			Author:      authors[authorIdx].Name,
			Entities:    &storyEntities,
			Keywords:    &storyKeywords,
			Language:    storyInDb.Language,
			PublishedAt: storyInDb.PublishedAt,
			Source:      sources[sourceIdx].Name,
			StoryId:     storyInDb.StoryId.String(),
			Summary:     storyInDb.Summary,
			Title:       *storyInDb.Title,
			Url:         *storyInDb.Url,
		}
	}
	return stories
}

func GetStoryDependencies(storiesInDb []models.StoryInDb) ([]models.Author, []models.Source, []models.Keyword, []models.Entity) {
	authorIdSet := map[*uuid.UUID]bool{}
	authorIds := make([]uuid.UUID, len(storiesInDb))
	sourceIdSet := map[*string]bool{}
	sourceIds := make([]string, len(storiesInDb))
	keywordSet := map[*string]bool{}
	keywordTexts := make([]string, 0)
	entitySet := map[*string]bool{}
	entityLinks := make([]string, 0)
	for i, storyInDb := range storiesInDb {
		_, ok := authorIdSet[storyInDb.AuthorId]
		if !ok {
			authorIds[i] = *storyInDb.AuthorId
			authorIdSet[storyInDb.AuthorId] = true
		}
		_, ok2 := sourceIdSet[storyInDb.SourceId]
		if !ok2 {
			sourceIds[i] = *storyInDb.SourceId
			sourceIdSet[storyInDb.SourceId] = true
		}
		for _, keyword := range *storyInDb.Keywords {
			_, ok := keywordSet[keyword.Text]
			if !ok {
				keywordTexts = append(keywordTexts, *keyword.Text)
				keywordSet[keyword.Text] = true
			}
		}
		for _, entity := range *storyInDb.Entities {
			_, ok := entitySet[entity.Links]
			if !ok {
				entityLinks = append(entityLinks, *entity.Links)
				entitySet[entity.Links] = true
			}
		}
	}
	authors := GetAuthorsByIds(authorIds)
	sources := GetSourcesByIds(sourceIds)
	keywords := GetKeywordsByTexts(keywordTexts, *storiesInDb[0].Language)
	entities := GetEntitiesByLinks(entityLinks)
	return authors, sources, keywords, entities
}

func UpdateFeedbackCounts(story_id uuid.UUID, feedbackType string) bool {
	mongoFilter := bson.M{"story_id": story_id}
	story, err := dbs.GetSingle[models.StoryInDb](storyCollection, mongoFilter)
	if err != nil {
		return false
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
		return false
	}
	return dbs.AddOrUpdateOne(authorCollection, story) > 0
}

func GetPublicStories(language string) []models.ShortStory {
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
	return BuildShortStoriesFromDB(dbs.GetGrouped[models.StoryInDb](storyCollection, mongoFilter, "source_id", -1, "", false))
}

func GetSingleStory(not_id_list []uuid.UUID, language string) (models.ShortStory, error) {
	if language == "" {
		language = "en"
	}
	mongoFilter := bson.M{
		"language": language,
		"published_at": bson.M{
			"$gte": primitive.NewDateTimeFromTime(time.Now().AddDate(0, 0, -PREVIOUS_DAYS_OF_NEWS)),
			"$lt":  primitive.NewDateTimeFromTime(time.Now()),
		},
		"story_id": bson.M{"$nin": not_id_list},
	}
	stories := dbs.Get[models.StoryInDb](storyCollection, mongoFilter, -1, "", false)
	if len(stories) == 0 {
		return models.ShortStory{}, errors.New("Could not find another story")
	}
	return BuildShortStoriesFromDB(stories)[0], nil
}

func GetReccomendedStories(userId string, language string) []models.ShortStory {
	if language == "" {
		language = "en"
	}
	if userId == "" {
		return GetPublicStories(language)
	}
	mongoFilter := bson.M{
		"language": language,
		"story_id": bson.M{},
	}
	readStoryIds := user.GetReadStoryIds(userId)
	if len(readStoryIds) > 0 {
		mongoFilter["story_id"].(bson.M)["$nin"] = readStoryIds
	}
	resp, err := http.Get(os.Getenv("ML_URL") +
		"/recommendations/" + userId + "/" + language)
	if err == nil {
		defer resp.Body.Close()
		var storyIds []uuid.UUID
		json.NewDecoder(resp.Body).Decode(&storyIds)
		isIds := make([]uuid.UUID, 0)
		for _, id := range storyIds {
			isIds = append(isIds, id)
		}
		mongoFilter["story_id"].(bson.M)["$in"] = isIds
		stories := dbs.Get[models.StoryInDb](storyCollection, mongoFilter, 12, "", false)
		return BuildShortStoriesFromDB(stories)
	}
	mongoFilter["published_at"] = bson.M{
		"$gte": primitive.NewDateTimeFromTime(time.Now().AddDate(0, 0, -PREVIOUS_DAYS_OF_NEWS)),
		"$lt":  primitive.NewDateTimeFromTime(time.Now()),
	}
	return BuildShortStoriesFromDB(dbs.GetGrouped[models.StoryInDb](storyCollection, mongoFilter, "source_id", -1, "", false))
}

func UpdateTFIndex(language string) []models.RankingData {
	mongoFilter := bson.M{
		"language": language,
		"published_at": bson.M{
			"$gte": primitive.NewDateTimeFromTime(time.Now().AddDate(0, 0, -PREVIOUS_DAYS_OF_NEWS)),
			"$lt":  primitive.NewDateTimeFromTime(time.Now()),
		},
	}
	stories := BuildStoriesFromDB(dbs.Get[models.StoryInDb](storyCollection, mongoFilter, -1, "", false))
	rankingData := make([]models.RankingData, len(stories))
	for idx, story := range stories {
		kerywords := *story.Keywords
		mostFrequentKeyword := kerywords[0]
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
		rankingData[idx] = models.RankingData{
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
		}
	}
	return rankingData
}
