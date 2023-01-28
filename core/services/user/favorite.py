from pydantic import BaseModel, Field
from typing import Tuple

from services import mongo
from shared import bson_id

FAVORITE_SOURCE_DB_COLLECTION_NAME = "FavoriteSource"
FAVORITE_AUTHOR_DB_COLLECTION_NAME = "FavoriteAuthor"
FAVORITE_KEYWORD_DB_COLLECTION_NAME = "FavoriteKeyword"
FAVORITE_ENTITY_DB_COLLECTION_NAME = "FavoriteEntity"


class Favorite(BaseModel):
  id: bson_id.ObjectIdStr = Field(None, alias="_id")
  user_id: str = None
  identifier: str  # SourceId for sources, author_id for Authors, Keywords for Keywords and links for Entities
  value: str
  is_favorite: bool = False
  is_deleted: bool = False
  is_recommended: bool = False
  is_added: bool = False
  relevancy_rate: float = 0.0
  language: str = None


class FavoriteItems(BaseModel):
  favorite_sources: Tuple[Favorite, ...]
  favorite_authors: Tuple[Favorite, ...]
  favorite_keywords: Tuple[Favorite, ...]
  favorite_entities: Tuple[Favorite, ...]


def get_favorites(user_id: str,
                  db_collection: str,
                  count: int,
                  language: str = None) -> Tuple[Favorite, ...]:
  """Retrieves favorites from Mongo for different collections.
    There are separate collections for the favorite authors, sources,
    keywords, and entities.

    Args:
        user_id: The user id for which there are favorites.
        db_collection: The collection of favorites to be used.
        count: Number of favorites to be returned.
        language: If provided, it filters results to be specific to the
          language.

    Returns:
        A tuple of the user's favorites for the given collection.

    """

  mongo_filter = {"user_id": user_id, "is_favorite": True, "is_deleted": False}
  if language:
    mongo_filter.update({"language": language})
  favorites = mongo.get(db_collection,
                        mongo_filter,
                        limit=count,
                        sort="relevancy_rate",
                        reverse=True)
  return tuple(Favorite(**favorite) for favorite in favorites)


def get_recommended_favorites(user_id: str,
                              db_collection: str,
                              count: int,
                              language: str = None) -> Tuple[Favorite, ...]:
  """Retrieves recommended favorites from Mongo for different collections.
    Favorites are recommended by sorting for the highest relevancy_rate.
    There are separate collections for the favorite authors, sources, keywords,
    and entities.

    Args:
        user_id: The user id for which to recommend favorites.
        db_collection: The collection of favorites to be used.
        count: Number of favorites to be returned.
        language: If provided, it filters results to be specific to the
          language.

    Returns:
        A tuple of recommended favorites for the given collection.

    """

  recommend_filter = {"is_deleted": False}
  user_deleted_filter = {"user_id": user_id, "is_deleted": True}
  if language:
    recommend_filter.update({"language": language})
    user_deleted_filter.update({"language": language})
  recommended = mongo.get_grouped(db_collection,
                                  recommend_filter,
                                  "identifier",
                                  limit=count,
                                  sort="relevancy_rate",
                                  reverse=True)
  for rec in recommended:
    rec.update({"is_recommended": True})
    rec.update({"is_favorite": False})
    rec.update({"is_added": False})
    rec.update({"user_id": user_id})
    rec.pop("_id", None)
    rec.pop("id", None)
  user_deleted = mongo.get(db_collection,
                           user_deleted_filter,
                           limit=count,
                           sort="relevancy_rate",
                           reverse=True)
  user_deleted_ids = tuple(deleted["identifier"] for deleted in user_deleted)
  return tuple(
      Favorite(**favorite) for favorite in recommended
      if favorite["identifier"] not in user_deleted_ids)


def get_hated(user_id: str,
                  db_collection: str,
                  count: int,
                  language: str = None) -> Tuple[Favorite, ...]:
  """Retrieves hated items from Mongo for different collections.
    There are separate collections for the favorite authors, sources,
    keywords, and entities.

    Args:
        user_id: The user id for which there are hated items.
        db_collection: The collection of hated items to be used.
        count: Number of hated items to be returned.
        language: If provided, it filters results to be specific to the
          language.

    Returns:
        A tuple of the user's hated items for the given collection.

    """

  mongo_filter = {"user_id": user_id, "is_favorite": False, "is_deleted": True}
  if language:
    mongo_filter.update({"language": language})
  favorites = mongo.get(db_collection,
                        mongo_filter,
                        limit=count,
                        sort="relevancy_rate",
                        reverse=True)
  return tuple(Favorite(**favorite) for favorite in favorites)


def get_favorite_items(user_id: str,
                       count: int,
                       language: str = None) -> FavoriteItems:
  """Packages the favorites from different collections into a grouped
  FavoriteItems object.

    Args:
        user_id: The user id for which to return favorite items.
        count: Number of favorites per collection to be returned.
        language: If provided, it filters results to be specific to the
          language.

    Returns:
        The user's favorites items object.

    """

  fav_sources = get_favorites(user_id, FAVORITE_SOURCE_DB_COLLECTION_NAME,
                              count, language)
  fav_authors = get_favorites(user_id, FAVORITE_AUTHOR_DB_COLLECTION_NAME,
                              count, language)
  fav_keywords = get_favorites(user_id, FAVORITE_KEYWORD_DB_COLLECTION_NAME,
                               count, language)
  fav_entities = get_favorites(user_id, FAVORITE_ENTITY_DB_COLLECTION_NAME,
                               count, language)
  return FavoriteItems(favorite_sources=fav_sources,
                       favorite_authors=fav_authors,
                       favorite_keywords=fav_keywords,
                       favorite_entities=fav_entities)


def get_recommended_favorite_items(user_id: str,
                                   count: int,
                                   language: str = None) -> FavoriteItems:
  """Packages the recommended favorites from different collections into a
  grouped FavoriteItems object.

    Args:
        user_id: The user id for which to return recommended favorite items.
        count: Number of recommended favorites per collection to be returned.
        language: If provided, it filters results to be specific to the
          language.

    Returns:
        The user's recommended favorites items object.

    """

  fav_sources = get_recommended_favorites(user_id,
                                          FAVORITE_SOURCE_DB_COLLECTION_NAME,
                                          count, language)
  fav_authors = get_recommended_favorites(user_id,
                                          FAVORITE_AUTHOR_DB_COLLECTION_NAME,
                                          count, language)
  fav_keywords = get_recommended_favorites(
      user_id, FAVORITE_KEYWORD_DB_COLLECTION_NAME, count, language)
  fav_entities = get_recommended_favorites(user_id,
                                           FAVORITE_ENTITY_DB_COLLECTION_NAME,
                                           count, language)
  return FavoriteItems(favorite_sources=fav_sources,
                       favorite_authors=fav_authors,
                       favorite_keywords=fav_keywords,
                       favorite_entities=fav_entities)


def get_hated_items(user_id: str,
                       count: int,
                       language: str = None) -> FavoriteItems:
  """Packages the hated items from different collections into a grouped
  FavoriteItems object.

    Args:
        user_id: The user id for which to return hated items.
        count: Number of hated items per collection to be returned.
        language: If provided, it filters results to be specific to the
          language.

    Returns:
        The user's hated items object.

    """

  fav_sources = get_hated(user_id, FAVORITE_SOURCE_DB_COLLECTION_NAME,
                              count, language)
  fav_authors = get_hated(user_id, FAVORITE_AUTHOR_DB_COLLECTION_NAME,
                              count, language)
  fav_keywords = get_hated(user_id, FAVORITE_KEYWORD_DB_COLLECTION_NAME,
                               count, language)
  fav_entities = get_hated(user_id, FAVORITE_ENTITY_DB_COLLECTION_NAME,
                               count, language)
  return FavoriteItems(favorite_sources=fav_sources,
                       favorite_authors=fav_authors,
                       favorite_keywords=fav_keywords,
                       favorite_entities=fav_entities)


def update_from_user(favorite: Favorite, db_collection: str):
  """A straight update of a favorite, which is configured directly by the
  user via the front-end.

    Args:
        favorite: The user configured favorite to be updated.
        db_collection: The database collection which needs to be updated.

    Returns:
        The results of the mongo operation.

    """

  return mongo.add_or_update(favorite.dict(), db_collection)


def update_from_story(user_id: str,
                      identifier: str,
                      value: str,
                      reward: float,
                      db_collection: str,
                      language: str = None):
  """An update of a favorite when it is found in a story.

    Args:
        user_id: The user id for the favorite to be updated.
        identifier: The identifying property of the favorite.
        value: The value of the favorite to be updated.
        reward: The amount for which to increase/decrease the relevancy rate by.
        db_collection: The database collection which needs to be updated.
        language: The language of the favorite to be updated.

    Returns:
        The results of the mongo operation.

    """

  mongo_filter = {"user_id": str(user_id), "identifier": str(identifier)}
  users_favorites = mongo.get(db_collection, mongo_filter)
  favorite = None
  if users_favorites:
    favorite = Favorite(**users_favorites[0])
    favorite.relevancy_rate += reward
  else:
    favorite = Favorite(user_id=str(user_id),
                        identifier=str(identifier),
                        value=value,
                        is_favorite=False,
                        is_deleted=False,
                        is_recommended=True,
                        is_added=False,
                        relevancy_rate=reward,
                        language=language)
  return mongo.add_or_update(favorite.dict(), db_collection)
