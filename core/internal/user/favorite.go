package user

import (
	"core/internal/dbs"
	"errors"

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
	language string) []Favorite {
	mongoFilter := bson.M{"user_id": userId, "is_favorite": true, "is_deleted": false}
	if language != "" {
		mongoFilter["language"] = language
	}
	return dbs.Get[Favorite](dbCollection, mongoFilter, count, "relevancy_rate", true)
}

func GetReccomendedFavorites(userId string,
	dbCollection string,
	count int64,
	language string) []Favorite {
	recommendFilter := bson.M{"user_id": bson.M{"$ne": userId}}
	if language != "" {
		recommendFilter["language"] = language
	}
	reccomended := dbs.GetGrouped[Favorite](dbCollection, recommendFilter, "identifier", count, "relevancy_rate", true)
	for i := range reccomended {
		reccomended[i].IsRecommended = true
		reccomended[i].IsFavorite = false
		reccomended[i].IsAdded = false
		reccomended[i].UserId = userId
		reccomended[i].Id = nil
	}
	return reccomended
}

func GetHated(userId string,
	dbCollection string,
	count int64,
	language string) []Favorite {
	mongoFilter := bson.M{"user_id": userId, "is_favorite": false, "is_deleted": true}
	if language != "" {
		mongoFilter["language"] = language
	}
	return dbs.Get[Favorite](dbCollection, mongoFilter, count, "relevancy_rate", true)
}

func GetFavoriteItems(userId string,
	count int64,
	language string) FavoriteItems {
	favSources := GetFavorites(userId, FAVORITE_SOURCE_DB_COLLECTION_NAME,
		count, language)
	favAuthors := GetFavorites(userId, FAVORITE_AUTHOR_DB_COLLECTION_NAME,
		count, language)
	favKeywords := GetFavorites(userId, FAVORITE_KEYWORD_DB_COLLECTION_NAME,
		count, language)
	favEntities := GetFavorites(userId, FAVORITE_ENTITY_DB_COLLECTION_NAME,
		count, language)
	return FavoriteItems{
		FavoriteSources:  favSources,
		FavoriteAuthors:  favAuthors,
		FavoriteKeywords: favKeywords,
		FavoriteEntities: favEntities,
	}
}

func GetReccomendedFavoriteItems(userId string,
	count int64,
	language string) FavoriteItems {
	favSources := GetReccomendedFavorites(userId, FAVORITE_SOURCE_DB_COLLECTION_NAME,
		count, language)
	favAuthors := GetReccomendedFavorites(userId, FAVORITE_AUTHOR_DB_COLLECTION_NAME,
		count, language)
	favKeywords := GetReccomendedFavorites(userId, FAVORITE_KEYWORD_DB_COLLECTION_NAME,
		count, language)
	favEntities := GetReccomendedFavorites(userId, FAVORITE_ENTITY_DB_COLLECTION_NAME,
		count, language)
	return FavoriteItems{
		FavoriteSources:  favSources,
		FavoriteAuthors:  favAuthors,
		FavoriteKeywords: favKeywords,
		FavoriteEntities: favEntities,
	}
}

func GetHatedItems(userId string,
	count int64,
	language string) FavoriteItems {
	favSources := GetHated(userId, FAVORITE_SOURCE_DB_COLLECTION_NAME,
		count, language)
	favAuthors := GetHated(userId, FAVORITE_AUTHOR_DB_COLLECTION_NAME,
		count, language)
	favKeywords := GetHated(userId, FAVORITE_KEYWORD_DB_COLLECTION_NAME,
		count, language)
	favEntities := GetHated(userId, FAVORITE_ENTITY_DB_COLLECTION_NAME,
		count, language)
	return FavoriteItems{
		FavoriteSources:  favSources,
		FavoriteAuthors:  favAuthors,
		FavoriteKeywords: favKeywords,
		FavoriteEntities: favEntities,
	}
}

func UpdateFromUser(favorite Favorite, dbCollection string) bool {
	return dbs.AddOrUpdateOne(dbCollection, favorite) > 0
}

func UpdateFromStory(userId string, identifier string, value string, reward float32, dbCollection string, language string) bool {
	mongoFilter := bson.M{"user_id": userId, "identifier": identifier, "language": language}
	usersFavorites := dbs.Get[Favorite](dbCollection, mongoFilter, -1, "", false)
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
		return "", errors.New("No Favorite Collection Found")
	}
}
