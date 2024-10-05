package story

import (
	"slices"
	"time"

	"core/pkg/dbs"
	"core/pkg/models"

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

func RemoveOldStories() {
	mongoFilter := bson.M{
		"published_at": bson.M{
			"$lte": primitive.NewDateTimeFromTime(time.Now().AddDate(0, 0, -STORY_DAYS_TO_EXPIRY)),
		},
	}
	dbs.Remove(storyCollection, mongoFilter)
}

func AddOrUpdateStories(stories []models.Story) {
	storyInterfaces := make([]interface{}, 0)
	for _, story := range stories {
		storyInterfaces = append(storyInterfaces, story)
	}
	dbs.Remove(storyCollection, storyInterfaces)
}

func GetStoryById(storyId string) models.Story {
	id, err := uuid.Parse(storyId)
	if err != nil {
		panic(err)
	}
	mongoFilter := bson.M{"story_id": id}
	return BuildStoriesFromDB(dbs.Get[models.StoryInDb](storyCollection, mongoFilter, 1, "", false))[0]
}

func BuildStoriesFromDB(storiesInDb []models.StoryInDb) []models.Story {
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
	stories := make([]models.Story, len(storiesInDb))
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

func UpdateFeedbackCounts(story_id uuid.UUID, feedbackType string) bool {
	mongoFilter := bson.M{"story_id": story_id}
	story := dbs.GetSingle[models.StoryInDb](storyCollection, mongoFilter)
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
