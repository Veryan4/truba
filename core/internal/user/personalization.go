package user

import (
	"errors"
	"sync"

	"core/internal/utils"
)

const FAVORITE_ITEM_COUNT = 10

type Personalization struct {
	RecommendedItems FavoriteItems `bson:"recommended_items,omitempty" json:"recommended_items,omitempty"`
	FavoriteItems    FavoriteItems `bson:"favorite_items,omitempty" json:"favorite_items,omitempty"`
	HatedItems       FavoriteItems `bson:"hated_items,omitempty" json:"hated_items,omitempty"`
}

func GetPersonalization(userId string, language string) (Personalization, error) {
	var recommendedItems FavoriteItems
	var favoriteItems FavoriteItems
	var hatedItems FavoriteItems
	var e1 error
	var e2 error
	var e3 error
	var waitGroup sync.WaitGroup
	waitGroup.Add(3)
	go func() {
		defer waitGroup.Done()
		f, e := GetFavoriteItems(userId, FAVORITE_ITEM_COUNT, language, GetRecommendedFavorites)
		recommendedItems = f
		e1 = e
	}()
	go func() {
		defer waitGroup.Done()
		f, e := GetFavoriteItems(userId, FAVORITE_ITEM_COUNT, language, GetFavorites)
		favoriteItems = f
		e2 = e
	}()
	go func() {
		defer waitGroup.Done()
		f, e := GetFavoriteItems(userId, FAVORITE_ITEM_COUNT, language, GetHated)
		hatedItems = f
		e3 = e
	}()
	waitGroup.Wait()
	if e1 != nil || e2 != nil || e3 != nil {
		return Personalization{}, utils.LogError(errors.New("error fetching Personalization"))
	}
	return Personalization{
		RecommendedItems: recommendedItems,
		FavoriteItems:    favoriteItems,
		HatedItems:       hatedItems,
	}, nil
}
