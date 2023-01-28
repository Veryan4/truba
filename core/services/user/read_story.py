from pydantic import BaseModel, Field
from typing import Tuple
from datetime import datetime, timedelta

from services import mongo

DB_COLLECTION_NAME = "ReadStory"
DAYS_OF_READ_STORIES = 1


class ReadStory(BaseModel):
  user_id: str
  story_id: str
  read_time: datetime = Field(default_factory=datetime.utcnow)


def add(read_story: ReadStory):
  """Straight adding of a ReadStory object to Mongo.

    Args:
        user_id: The user's id for which the Personalization object is returned.
        language: The language for which the Personalization object is returned.

    Returns:
        The user's Personalization object.

    """

  return mongo.add_or_update(read_story.dict(), DB_COLLECTION_NAME)


def get_story_ids(user_id: str) -> Tuple[str, ...]:
  """Retrieve the ids of stories that have been read by the user within the
  last n days.

    Args:
        user_id: The user's id for which stories have been read.

    Returns:
        The ids of stories that have been read by the user.

    """

  end = datetime.utcnow()
  delta = timedelta(days=DAYS_OF_READ_STORIES)
  start = end - delta
  mongo_filter = {"user_id": user_id, "read_time": {'$gte': start, '$lt': end}}
  read_stories = mongo.get(DB_COLLECTION_NAME, mongo_filter)
  if read_stories:
    return tuple(set(read_story["story_id"] for read_story in read_stories))
  return ()
