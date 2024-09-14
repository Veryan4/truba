from typing import Tuple

from services import mongo
import project_types

DB_COLLECTION_NAME = "Keyword"


def add_new_keywords(keywords: Tuple[project_types.Keyword, ...]):
  """Stores new keywords to the Mongo database.

    Args:
        keywords: The keywords to store.

    Returns:
        If there are new keywords to add it returns the Mongo result,
        otherwise it returns None.

    """

  keyword_texts = set()
  unique_keywords = tuple(
      keyword_texts.add(word.text) or word for word in keywords
      if word.text not in keyword_texts)
  # search to see whether the keyword already exists in db
  new_keyword_texts = tuple(keyword.text for keyword in unique_keywords)
  mongo_filter = {"text": {"$in": new_keyword_texts}}
  current_keywords = mongo.get(DB_COLLECTION_NAME, mongo_filter)
  current_keyword_texts = tuple(keyword["text"]
                                for keyword in current_keywords)
  keywords_to_push = tuple(keyword.dict() for keyword in unique_keywords
                           if keyword.text not in current_keyword_texts)
  if keywords_to_push:
    return mongo.add_or_update(keywords_to_push, DB_COLLECTION_NAME)
  return None


def get_by_texts(keyword_texts: Tuple[str, ...],
                 language: str = "en") -> Tuple[project_types.Keyword]:
  """Retrieves a list of keywords from the database given their ids.

    Args:
        keyword_ids: The list of keyword ids.

    Returns:
        The Authors if found, otherwise None.

    """

  mongo_filter = {"text": {"$in": list(keyword_texts)}, "language": language}
  keywords = mongo.get(DB_COLLECTION_NAME,
                       mongo_filter,
                       limit=len(keyword_texts))
  return tuple(project_types.Keyword(**keyword) for keyword in keywords)
