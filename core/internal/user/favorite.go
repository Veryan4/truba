package user

import (
	"errors"
	"sync"

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
	IsFavorite    *bool               `bson:"is_favorite,omitempty" json:"is_favorite,omitempty"`
	IsDeleted     *bool               `bson:"is_deleted,omitempty" json:"is_deleted,omitempty"`
	IsRecommended *bool               `bson:"is_recommended,omitempty" json:"is_recommended,omitempty"`
	IsAdded       *bool               `bson:"is_added,omitempty" json:"is_added,omitempty"`
	RelevancyRate float32             `bson:"relevancy_rate,omitempty" json:"relevancy_rate,omitempty"`
	Language      string              `bson:"language,omitempty" json:"language,omitempty"`
}

type FavoriteItems struct {
	FavoriteSources  []Favorite `bson:"favorite_sources,omitempty" json:"favorite_sources,omitempty"`
	FavoriteAuthors  []Favorite `bson:"favorite_authors,omitempty" json:"favorite_authors,omitempty"`
	FavoriteKeywords []Favorite `bson:"favorite_keywords,omitempty" json:"favorite_keywords,omitempty"`
	FavoriteEntities []Favorite `bson:"favorite_entities,omitempty" json:"favorite_entities,omitempty"`
}

type FavoriteItemGetter func(userId string,
	dbCollection string,
	count int64,
	language string) ([]Favorite, error)

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
	falsy := false
	truthy := true
	for i := range recommended {
		recommended[i].IsRecommended = &truthy
		recommended[i].IsFavorite = &falsy
		recommended[i].IsAdded = &falsy
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
	language string,
	getter FavoriteItemGetter) (FavoriteItems, error) {
	var favSources []Favorite
	var favAuthors []Favorite
	var favKeywords []Favorite
	var favEntities []Favorite
	var e1 error
	var e2 error
	var e3 error
	var e4 error
	var waitGroup sync.WaitGroup
	waitGroup.Add(4)
	go func() {
		defer waitGroup.Done()
		f, e := getter(userId, FAVORITE_SOURCE_DB_COLLECTION_NAME,
			count, language)
		favSources = f
		e1 = e
	}()
	go func() {
		defer waitGroup.Done()
		f, e := getter(userId, FAVORITE_AUTHOR_DB_COLLECTION_NAME,
			count, language)
		favAuthors = f
		e2 = e
	}()
	go func() {
		defer waitGroup.Done()
		f, e := getter(userId, FAVORITE_KEYWORD_DB_COLLECTION_NAME,
			count, language)
		favKeywords = f
		e3 = e
	}()
	go func() {
		defer waitGroup.Done()
		f, e := getter(userId, FAVORITE_ENTITY_DB_COLLECTION_NAME,
			count, language)
		favEntities = f
		e4 = e
	}()
	waitGroup.Wait()
	if e1 != nil || e2 != nil || e3 != nil || e4 != nil {
		return FavoriteItems{}, utils.LogError(errors.New("error creating favorite items"))
	}
	return FavoriteItems{
		FavoriteSources:  favSources,
		FavoriteAuthors:  favAuthors,
		FavoriteKeywords: favKeywords,
		FavoriteEntities: favEntities,
	}, nil
}

func UpdateFavoriteFromUser(favorite Favorite, dbCollection string) error {
	mongoFilter := bson.M{"user_id": favorite.UserId, "identifier": favorite.Identifier, "language": favorite.Language}
	var usersFavorite Favorite
	err := dbs.GetSingle(dbCollection, mongoFilter, &usersFavorite)
	if err == nil {
		usersFavorite.IsAdded = favorite.IsAdded
		usersFavorite.IsDeleted = favorite.IsDeleted
		usersFavorite.IsFavorite = favorite.IsFavorite
		usersFavorite.IsRecommended = favorite.IsRecommended
		usersFavorite.RelevancyRate = favorite.RelevancyRate
		return dbs.AddOrUpdateOne(dbCollection, usersFavorite)
	}
	falsy := false
	createFavorite := Favorite{
		UserId:        favorite.UserId,
		Identifier:    favorite.Identifier,
		Value:         favorite.Value,
		IsFavorite:    &falsy,
		IsDeleted:     &falsy,
		IsRecommended: &falsy,
		IsAdded:       &falsy,
		RelevancyRate: favorite.RelevancyRate,
		Language:      favorite.Language,
	}
	if favorite.IsFavorite != nil {
		createFavorite.IsFavorite = favorite.IsFavorite
	}
	if favorite.IsDeleted != nil {
		createFavorite.IsDeleted = favorite.IsDeleted
	}
	if favorite.IsRecommended != nil {
		createFavorite.IsRecommended = favorite.IsRecommended
	}
	if favorite.IsAdded != nil {
		createFavorite.IsAdded = favorite.IsAdded
	}
	return dbs.AddOrUpdateOne(dbCollection, createFavorite)
}

func UpdateFavoriteFromStory(userId string, identifier string, value string, reward float32, dbCollection string, language string) error {
	mongoFilter := bson.M{"user_id": userId, "identifier": identifier, "language": language}
	var usersFavorite Favorite
	err := dbs.GetSingle(dbCollection, mongoFilter, &usersFavorite)
	if err == nil {
		usersFavorite.RelevancyRate += reward
		return dbs.AddOrUpdateOne(dbCollection, usersFavorite)
	}
	falsy := false
	truthy := true
	favorite := Favorite{
		UserId:        userId,
		Identifier:    identifier,
		Value:         value,
		IsFavorite:    &falsy,
		IsDeleted:     &falsy,
		IsRecommended: &truthy,
		IsAdded:       &falsy,
		RelevancyRate: reward,
		Language:      language,
	}
	return dbs.AddOrUpdateOne(dbCollection, favorite)
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
		return "", utils.LogError(errors.New("no Favorite Collection Found"))
	}
}
