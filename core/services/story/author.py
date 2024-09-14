from uuid import UUID
from typing import Tuple, Optional

from services import mongo
import project_types

DB_COLLECTION_NAME = "Author"


def add_new_authors(authors: Tuple[project_types.Author, ...]):
  """Stores new Authors to the Mongo database.

    Args:
        authors: The Authors to store.

    Returns:
        If there are new Authors to add it returns the Mongo result,
        otherwise it returns None. 

    """

  author_ids = set()
  unique_authors = tuple(
      author_ids.add(author.author_id) or author for author in authors
      if author.author_id not in author_ids)
  # search to see whether the author already exists in db
  new_author_ids = tuple(a.author_id for a in unique_authors)
  mongo_filter = {"author_id": {"$in": new_author_ids}}
  current_authors = mongo.get(DB_COLLECTION_NAME, mongo_filter)
  current_author_ids = tuple(a["author_id"] for a in current_authors)
  authors_to_push = tuple(a.dict() for a in unique_authors
                          if a.author_id not in current_author_ids)
  if authors_to_push:
    return mongo.add_or_update(authors_to_push, DB_COLLECTION_NAME)
  return None


def get_by_name(author_name: str) -> Optional[project_types.Author]:
  """Retrieves an Author fom the database given its name.

    Args:
        author_name: The name of the author.

    Returns:
        The Author if found, otherwise None.

    """

  mongo_filter = {"name": author_name}
  authors = mongo.get(DB_COLLECTION_NAME, mongo_filter, limit=1)
  if authors:
    return project_types.Author(**authors[0])
  return None


def get_by_id(author_id: str) -> Optional[project_types.Author]:
  """Retrieves an Author from the database given its id.

    Args:
        author_id: The id of the author.

    Returns:
        The Author if found, otherwise None.

    """

  mongo_filter = {"author_id": UUID(author_id)}
  authors = mongo.get(DB_COLLECTION_NAME, mongo_filter, limit=1)
  if authors:
    return project_types.Author(**authors[0])
  return None


def get_by_ids(author_ids: Tuple[UUID, ...]) -> Tuple[project_types.Author]:
  """Retrieves a list of Authors from the database given their ids.

    Args:
        author_ids: The list of author ids.

    Returns:
        The Authors if found, otherwise None.

    """

  mongo_filter = {"author_id": {"$in": list(author_ids)}}
  authors = mongo.get(DB_COLLECTION_NAME, mongo_filter, limit=len(author_ids))
  return tuple(project_types.Author(**author) for author in authors)


def update_reputation(author_id: UUID, reward: float):
  """Updates the Author's reputation score.

    Args:
        author_id: The id of the author.
        reward: The score to add/subtract from the author's reputation

    Returns:
        The Mongo result if successful, otherwise None.

    """

  mongo_filter = {"author_id": author_id}
  authors = mongo.get(DB_COLLECTION_NAME, mongo_filter, limit=1)
  if authors:
    author = authors[0]
    author["reputation"] += reward
    return mongo.add_or_update(author, DB_COLLECTION_NAME)
  return None
