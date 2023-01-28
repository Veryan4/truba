from pydantic import BaseModel
from multiprocessing import Pool
from typing import Tuple, Optional, List
from uuid import UUID
import requests

from services.user import user, favorite
from shared import setup

FAVORITE_ITEM_COUNT = 10

class IgnoreItems(BaseModel):
  sources: List[str]
  authors: List[UUID]
  keywords: List[str]
  entities: List[str]


class Personalization(BaseModel):
  recommended_items: favorite.FavoriteItems
  favorite_items: favorite.FavoriteItems
  hated_items: favorite.FavoriteItems


def get_personalization(user_id: str, language: str) -> Personalization:
  """Retrieves the Personalization object, which is used by the user to
  configure their recommendations.

    Args:
        user_id: The user's id for which the Personalization object is returned.
        language: The language for which the Personalization object is returned.

    Returns:
        The user's Personalization object.

    """
  
  pool = Pool(processes=3)
  arg = [user_id, FAVORITE_ITEM_COUNT, language]
  future_1 = pool.map_async(favorite.get_recommended_favorite_items, arg)
  future_2 = pool.map_async(favorite.get_favorite_items, arg)
  future_3 = pool.map_async(favorite.get_hated_items, arg)
  recommended_items = future_1.get()
  favorite_items = future_2.get()
  hated_items = future_3.get()
  pool.close()
  pool.join()

  return Personalization(recommended_items=recommended_items,
                         favorite_items=favorite_items,
                         hated_items=hated_items)


#TODO: For eventual Solr implementation
def add_solr_model(model_id: str):
  res = requests.get(setup.get_base_ml_service_url() + "/model-store/" +
                     model_id)
  return res


#TODO: For eventual Solr implementation
def compare_favorites(users_favorites: Tuple[str, ...],
                      others_favorites: Tuple[str, ...]) -> float:
  divider = float(len(set(users_favorites) | set(others_favorites)))
  if divider != 0:
    return len(set(users_favorites) & set(others_favorites)) / divider
  return 0.0


#TODO: For eventual Solr implementation
#Needs to be figured out at DB level for performance
def find_most_similar_profile(
    users_favorite_items: favorite.FavoriteItems) -> Optional[str]:
  users_sources = tuple(s.identifier
                        for s in users_favorite_items.favorite_sources)
  users_authors = tuple(a.identifier
                        for a in users_favorite_items.favorite_authors)
  users_entities = tuple(e.identifier
                         for e in users_favorite_items.favorite_entities)
  users_keywords = tuple(k.identifier
                         for k in users_favorite_items.favorite_keywords)
  lowest_value = 0.0
  similar_profiles = {}
  user_ids = user.get_ids()
  for user_id in user_ids:
    others_favorite_items = favorite.get_favorite_items(user_id, 5)
    others_sources = tuple(s.identifier
                           for s in others_favorite_items.favorite_sources)
    others_authors = tuple(a.identifier
                           for a in others_favorite_items.favorite_authors)
    others_entities = tuple(e.identifier
                            for e in others_favorite_items.favorite_entities)
    others_keywords = tuple(k.identifier
                            for k in others_favorite_items.favorite_keywords)
    sources_score = compare_favorites(users_sources, others_sources)
    authors_score = compare_favorites(users_authors, others_authors)
    entities_score = compare_favorites(users_entities, others_entities)
    keywords_score = compare_favorites(users_keywords, others_keywords)
    average_score = (sources_score + authors_score + entities_score +
                     keywords_score) / 4
    if average_score <= lowest_value:
      continue
    lowest_value = average_score
    similar_profiles.update({user_id: average_score})
  if similar_profiles:
    similar_profiles = {
        k: v
        for k, v in sorted(
            similar_profiles.items(), key=lambda item: item[1], reverse=True)
    }
    similar_id = next(iter(similar_profiles))
    if similar_profiles[similar_id] > 0:
      return similar_id
  return None
