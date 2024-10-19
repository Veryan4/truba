package user

import (
	"core/internal/dbs"
	"core/internal/utils"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

const FAVORITE_SOURCE_DB_COLLECTION_NAME = "FavoriteSource"
const FAVORITE_AUTHOR_DB_COLLECTION_NAME = "FavoriteAuthor"
const FAVORITE_KEYWORD_DB_COLLECTION_NAME = "FavoriteKeyword"
const FAVORITE_ENTITY_DB_COLLECTION_NAME = "FavoriteEntity"

type Favorite struct {
	Id            *primitive.ObjectID `bson:"_id,omitempty" json:"_id,omitempty"`
	UserId        string              `bson:"user_id,omitempty" json:"user_id,omitempty"`
	Identifier    string              `bson:"identifier,omitempty" json:"identifier,omitempty"`
	Value         string              `bson:"value,omitempty" json:"value,omitempty"`
	IsFavorite    bool                `bson:"is_favorite,omitempty" json:"is_favorite,omitempty"`
	IsDeleted     bool                `bson:"is_deleted,omitempty" json:"is_deleted,omitempty"`
	IsRecommended bool                `bson:"is_recommended,omitempty" json:"is_recommended,omitempty"`
	IsAdded       bool                `bson:"is_added,omitempty" json:"is_added,omitempty"`
	RelevancyRate float32             `bson:"relevancy_rate,omitempty" json:"relevancy_rate,omitempty"`
	Language      string              `bson:"language,omitempty" json:"language,omitempty"`
}

type FavoriteItems struct {
	FavoriteSources  []Favorite `bson:"favorite_sources,omitempty" json:"favorite_sources,omitempty"`
	FavoriteAuthors  []Favorite `bson:"favorite_authors,omitempty" json:"favorite_authors,omitempty"`
	FavoriteKeywords []Favorite `bson:"favorite_keywords,omitempty" json:"favorite_keywords,omitempty"`
	FavoriteEntities []Favorite `bson:"favorite_entities,omitempty" json:"favorite_entities,omitempty"`
}

func GetFavorites(userId string,
	dbCollection string,
	count int64,
	language string) ([]Favorite, error) {
	mongoFilter := bson.M{"user_id": userId, "is_favorite": true, "is_deleted": false}
	if language != "" {
		mongoFilter["language"] = language
	}
	var favorites []Favorite
	err := dbs.GetSorted(dbCollection, mongoFilter, &favorites, "relevancy_rate", true, count)
	return favorites, err
}

func GetRecommendedFavorites(userId string,
	dbCollection string,
	count int64,
	language string) ([]Favorite, error) {
	recommendFilter := bson.M{"user_id": bson.M{"$ne": userId}}
	if language != "" {
		recommendFilter["language"] = language
	}
	var recommended []Favorite
	err := dbs.GetGrouped(dbCollection, recommendFilter, &recommended, "identifier", count, "relevancy_rate", true)
	if err != nil {
		return recommended, err
	}
	for i := range recommended {
		recommended[i].IsRecommended = true
		recommended[i].IsFavorite = false
		recommended[i].IsAdded = false
		recommended[i].UserId = userId
		recommended[i].Id = nil
	}
	return recommended, nil
}

func GetHated(userId string,
	dbCollection string,
	count int64,
	language string) ([]Favorite, error) {
	mongoFilter := bson.M{"user_id": userId, "is_favorite": false, "is_deleted": true}
	if language != "" {
		mongoFilter["language"] = language
	}
	var recommended []Favorite
	err := dbs.GetSorted(dbCollection, mongoFilter, &recommended, "relevancy_rate", true, count)
	return recommended, err
}

func GetFavoriteItems(userId string,
	count int64,
	language string) (FavoriteItems, error) {
	favSources, e1 := GetFavorites(userId, FAVORITE_SOURCE_DB_COLLECTION_NAME,
		count, language)
	favAuthors, e2 := GetFavorites(userId, FAVORITE_AUTHOR_DB_COLLECTION_NAME,
		count, language)
	favKeywords, e3 := GetFavorites(userId, FAVORITE_KEYWORD_DB_COLLECTION_NAME,
		count, language)
	favEntities, e4 := GetFavorites(userId, FAVORITE_ENTITY_DB_COLLECTION_NAME,
		count, language)
	if e1 != nil || e2 != nil || e3 != nil || e4 != nil {
		return FavoriteItems{}, utils.LogError("error creating favorite items")
	}
	return FavoriteItems{
		FavoriteSources:  favSources,
		FavoriteAuthors:  favAuthors,
		FavoriteKeywords: favKeywords,
		FavoriteEntities: favEntities,
	}, nil
}

func GetRecommendedFavoriteItems(userId string,
	count int64,
	language string) (FavoriteItems, error) {
	favSources, e1 := GetRecommendedFavorites(userId, FAVORITE_SOURCE_DB_COLLECTION_NAME,
		count, language)
	favAuthors, e2 := GetRecommendedFavorites(userId, FAVORITE_AUTHOR_DB_COLLECTION_NAME,
		count, language)
	favKeywords, e3 := GetRecommendedFavorites(userId, FAVORITE_KEYWORD_DB_COLLECTION_NAME,
		count, language)
	favEntities, e4 := GetRecommendedFavorites(userId, FAVORITE_ENTITY_DB_COLLECTION_NAME,
		count, language)
	if e1 != nil || e2 != nil || e3 != nil || e4 != nil {
		return FavoriteItems{}, utils.LogError("error creating recommended items")
	}
	return FavoriteItems{
		FavoriteSources:  favSources,
		FavoriteAuthors:  favAuthors,
		FavoriteKeywords: favKeywords,
		FavoriteEntities: favEntities,
	}, nil
}

func GetHatedItems(userId string,
	count int64,
	language string) (FavoriteItems, error) {
	favSources, e1 := GetHated(userId, FAVORITE_SOURCE_DB_COLLECTION_NAME,
		count, language)
	favAuthors, e2 := GetHated(userId, FAVORITE_AUTHOR_DB_COLLECTION_NAME,
		count, language)
	favKeywords, e3 := GetHated(userId, FAVORITE_KEYWORD_DB_COLLECTION_NAME,
		count, language)
	favEntities, e4 := GetHated(userId, FAVORITE_ENTITY_DB_COLLECTION_NAME,
		count, language)
	if e1 != nil || e2 != nil || e3 != nil || e4 != nil {
		return FavoriteItems{}, utils.LogError("error creating hated items")
	}
	return FavoriteItems{
		FavoriteSources:  favSources,
		FavoriteAuthors:  favAuthors,
		FavoriteKeywords: favKeywords,
		FavoriteEntities: favEntities,
	}, nil
}

func UpdateFromUser(favorite Favorite, dbCollection string) bool {
	return dbs.AddOrUpdateOne(dbCollection, favorite) > 0
}

func UpdateFromStory(userId string, identifier string, value string, reward float32, dbCollection string, language string) bool {
	mongoFilter := bson.M{"user_id": userId, "identifier": identifier, "language": language}
	var usersFavorites []Favorite
	err := dbs.GetMany(dbCollection, mongoFilter, &usersFavorites)
	if err != nil {
		utils.LogError("Failed to fetch user favorites when updating from story")
		return false
	}
	var favorite Favorite
	if len(usersFavorites) > 0 {
		favorite = usersFavorites[0]
		favorite.RelevancyRate += reward
	} else {
		favorite = Favorite{
			UserId:        userId,
			Identifier:    identifier,
			Value:         value,
			IsFavorite:    false,
			IsDeleted:     false,
			IsRecommended: true,
			IsAdded:       false,
			RelevancyRate: reward,
			Language:      language,
		}
	}
	return dbs.AddOrUpdateOne(dbCollection, favorite) > 0
}

func GetFavoriteCollection(collection string) (string, error) {
	switch collection {
	case "source":
		return FAVORITE_SOURCE_DB_COLLECTION_NAME, nil
	case "author":
		return FAVORITE_AUTHOR_DB_COLLECTION_NAME, nil
	case "keyword":
		return FAVORITE_KEYWORD_DB_COLLECTION_NAME, nil
	case "entity":
		return FAVORITE_ENTITY_DB_COLLECTION_NAME, nil
	default:
		return "", utils.LogError("No Favorite Collection Found")
	}
}
