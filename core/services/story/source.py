import json
import requests
import os
from typing import Tuple, Optional

from services import mongo
from shared.types import source_types

DB_COLLECTION_NAME = "Source"


def add_new_sources(sources: Tuple[source_types.Source, ...]):
  """Stores new sources to the Mongo database.

    Args:
        sources: The sources to store.

    Returns:
        If there are new sources to add it returns the Mongo result,
        otherwise it returns None.

    """

  source_names = set()
  unique_sources = tuple(
      source_names.add(source.name) or source for source in sources
      if source.name not in source_names)
  new_source_names = tuple(n.name for n in unique_sources)
  mongo_filter = {"name": {"$in": new_source_names}}
  current_sources = mongo.get(DB_COLLECTION_NAME, mongo_filter)
  current_source_names = tuple(s["name"] for s in current_sources)
  sources_to_push = tuple(s.dict() for s in unique_sources
                          if s.name not in current_source_names)
  if sources_to_push:
    return mongo.add_or_update(sources_to_push, DB_COLLECTION_NAME)
  return None


def get_by_name(source_name: str) -> Optional[source_types.Source]:
  """Retrieves the source from the database by name.

    Args:
        source_name: The name of the source.

    Returns:
        The source if found, otherwise None.

    """

  mongo_filter = {"name": source_name}
  sources = mongo.get(DB_COLLECTION_NAME, mongo_filter, limit=1)
  if sources:
    return source_types.Source(**sources[0])
  return None


def get_by_id(source_id: str) -> Optional[source_types.Source]:
  """Retrieves the source from the database by id.

    Args:
        source_id: The id of the source.

    Returns:
        The source if found, otherwise None.

    """

  mongo_filter = {"source_id": source_id}
  sources = mongo.get(DB_COLLECTION_NAME, mongo_filter, limit=1)
  if sources:
    return source_types.Source(**sources[0])
  return None


def get_by_ids(source_ids: Tuple[str, ...]) -> Tuple[source_types.Source]:
  """Retrieves a list of Sources from the database given their ids.

    Args:
        source_ids: The list of source ids.

    Returns:
        The Sources if found, otherwise None.

    """

  mongo_filter = {"source_id": {"$in": list(source_ids)}}
  sources = mongo.get(DB_COLLECTION_NAME, mongo_filter, limit=len(source_ids))
  return tuple(source_types.Source(**source) for source in sources)


def get_source_name(source_id: str) -> Optional[source_types.Source]:
  """Retrieves a sources name given its id.

    Args:
        source_id: The id of the source.

    Returns:
        The source's name if found, otherwise None.

    """

  mongo_filter = {"source_id": source_id}
  sources = mongo.get(DB_COLLECTION_NAME, mongo_filter, limit=1)
  if sources:
    return sources[0]["name"]
  return None


def get_all_sources(language: str) -> Tuple[source_types.Source, ...]:
  """Retrieves a sources name given its id.

    Args:
        source_id: The id of the source.

    Returns:
        The source's name if found, otherwise None.

    """

  mongo_filter = {"language": language}
  sources = mongo.get(DB_COLLECTION_NAME, mongo_filter)
  if not sources:
    reset_sources()
    sources = mongo.get(DB_COLLECTION_NAME, mongo_filter)
  return tuple(source_types.Source(**source) for source in sources)


def reset_sources():
  """Removes then reloads sources. An attempt is made to extract the sources
  from an airtable. If that fails, the sources are loaded from static data in
  a JSON file.

    Returns:
        The mongo result from adding the sources or None if failed to reset

    """

  sources_to_push = None
  try:
    api_key = "Bearer " + os.getenv("AIRTABLE_API_KEY")
    response = requests.get("https://api.airtable.com/v0/" +
                            os.getenv("AIRTABLE_ID") + "/Sources",
                            headers={"Authorization": api_key})
    if response:
      sources_dict = response.json()
      sources_list = tuple(
          source_types.Source(**source["fields"])
          for source in sources_dict["records"])
  except Exception:
    with open('../../data/scraper_data/sources_list.json') as json_file:
      sources_dict = json.load(json_file)
      sources = sources_dict["sources"]
      sources_list = tuple(source_types.Source(**source) for source in sources)
      sources_to_push = tuple(s.dict() for s in sources_list)
  if sources_to_push:
    mongo.remove(DB_COLLECTION_NAME, {})
    return mongo.add_or_update(sources_to_push, DB_COLLECTION_NAME)
  return None


def update_reputation(source_id: str, reward: float):
  """Updates the source's reputation score.

    Args:
        source_id: The id of the source.
        reward: The score to add/subtract from the source's reputation

    Returns:
        The Mongo result if successful, otherwise None.

    """

  mongo_filter = {"source_id": source_id}
  sources = mongo.get(DB_COLLECTION_NAME, mongo_filter, limit=1)
  if sources:
    source = sources[0]
    source["reputation"] += reward
    return mongo.add_or_update(source, DB_COLLECTION_NAME)
  return None
