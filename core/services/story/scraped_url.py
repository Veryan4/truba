from datetime import datetime, timedelta
from typing import Tuple

from services import mongo
import project_types

DB_COLLECTION_NAME = "ScrapedUrl"
DAYS_OF_PREVIOUSLY_SCRAPED = 3


def add_scraped_urls(scraped_urls: Tuple[project_types.ScrapedUrl, ...]):
  """Adds urls which have been scraped to the database.

    Args:
        scraped_urls: urls which have been scraped.

    Returns:
        The mongo result of the storing operation.

    """

  urls_to_push = tuple(m.dict() for m in scraped_urls)
  return mongo.add_or_update(urls_to_push, DB_COLLECTION_NAME)


def get_by_source_name(source_name: str) -> Tuple[str, ...]:
  """Retrieves the previously scraped urls given a source's name within
  the last n amount of days.

    Args:
        scraped_urls: urls which have been scraped.

    Returns:
        A Tuple of the previously scraped urls.

    """

  end = datetime.utcnow()
  delta = timedelta(days=DAYS_OF_PREVIOUSLY_SCRAPED)
  start = end - delta
  mongo_filter = {
      "source_name": source_name,
      "published_at": {
          '$gte': start,
          '$lt': end
      }
  }
  scraped_urls = mongo.get(DB_COLLECTION_NAME, mongo_filter)
  if scraped_urls:
    return tuple(s["url"] for s in scraped_urls)
  return tuple()
