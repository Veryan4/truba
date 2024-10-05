package user

const FAVORITE_ITEM_COUNT = 10

type Personalization struct {
	RecommendedItems FavoriteItems `bson:"recommended_items,omitempty" json:"recommended_items,omitempty"`
	FavoriteItems    FavoriteItems `bson:"favorite_items,omitempty" json:"favorite_items,omitempty"`
	HatedItems       FavoriteItems `bson:"hated_items,omitempty" json:"hated_items,omitempty"`
}

func GetPersonalization(userId string, language string) Personalization {
	reccomendedItems := GetReccomendedFavoriteItems(userId, FAVORITE_ITEM_COUNT, language)
	favoriteItems := GetFavoriteItems(userId, FAVORITE_ITEM_COUNT, language)
	hatedItems := GetHatedItems(userId, FAVORITE_ITEM_COUNT, language)
	return Personalization{
		RecommendedItems: reccomendedItems,
		FavoriteItems:    favoriteItems,
		HatedItems:       hatedItems,
	}
}
