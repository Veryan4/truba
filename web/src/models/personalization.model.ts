import { FavoriteItem } from "./favorite-item.model";

export class Personalization {
  favorite_keywords: FavoriteItem[];
  favorite_entities: FavoriteItem[];
  favorite_sources: FavoriteItem[];
  favorite_authors: FavoriteItem[];
}

export class Recommendation {
  recommended_items: Personalization;
  favorite_items: Personalization;

  constructor(recommendation: any) {
    this.recommended_items = this.mapFavoriteItems(
      recommendation.recommended_items
    );
    this.favorite_items = this.mapFavoriteItems(recommendation.favorite_items);
  }

  private mapFavoriteItems(personalization: any): Personalization {
    return {
      favorite_keywords: personalization.favorite_keywords,
      favorite_entities: personalization.favorite_entities,
      favorite_sources: personalization.favorite_sources,
      favorite_authors: personalization.favorite_authors,
    };
  }
}
