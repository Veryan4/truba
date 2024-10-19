package user

import "core/internal/utils"

const FAVORITE_ITEM_COUNT = 10

type Personalization struct {
	RecommendedItems FavoriteItems `bson:"recommended_items,omitempty" json:"recommended_items,omitempty"`
	FavoriteItems    FavoriteItems `bson:"favorite_items,omitempty" json:"favorite_items,omitempty"`
	HatedItems       FavoriteItems `bson:"hated_items,omitempty" json:"hated_items,omitempty"`
}

func GetPersonalization(userId string, language string) (Personalization, error) {
	recommendedItems, e1 := GetRecommendedFavoriteItems(userId, FAVORITE_ITEM_COUNT, language)
	favoriteItems, e2 := GetFavoriteItems(userId, FAVORITE_ITEM_COUNT, language)
	hatedItems, e3 := GetHatedItems(userId, FAVORITE_ITEM_COUNT, language)
	if e1 != nil || e2 != nil || e3 != nil {
		return Personalization{}, utils.LogError("error Personalization")
	}
	return Personalization{
		RecommendedItems: recommendedItems,
		FavoriteItems:    favoriteItems,
		HatedItems:       hatedItems,
	}, nil
}
