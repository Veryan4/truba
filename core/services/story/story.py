from uuid import UUID
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict
import requests

from services.search import features
from services.story import author, source, entity, keyword
from services.user import read_story
from services import mongo
from shared.types import story_types, data_set_types
from shared import setup

DB_COLLECTION_NAME = "Story"
STORY_DAYS_TO_EXPIRY = 90
PREVIOUS_DAYS_OF_NEWS = 1
RANKING_DATA_FAVORITE_COUNT = 50


def insert_stories(stories: Tuple[story_types.Story, ...]):
  """Adds new stories to the database as well as new authors if
  they are found within the stories.

  Args:
      stories: The stories to store.

  """

  authors = []
  keywords = []
  entities = []
  for story in stories:
    authors.append(story.author)
    for word in story.keywords:
      keywords.append(word.keyword)
    for ent in story.entities:
      entities.append(ent.entity)

  author.add_new_authors(tuple(authors))
  entity.add_new_entities(tuple(entities))
  keyword.add_new_keywords(tuple(keywords))

  add_or_update_stories(stories)
  remove_old_stories()


def remove_old_stories():
  """Removes stories from the database that are older than n days.
  This prevents the database from flooding.

    Args:
        stories: The stories to store.

    """

  now = datetime.utcnow()
  delta = timedelta(days=STORY_DAYS_TO_EXPIRY)
  start = now - delta
  mongo_filter = {"published_at": {"$lte": start}}
  mongo.remove(DB_COLLECTION_NAME, mongo_filter)


def build_stories_from_db(
    stories_in_db: Tuple[Dict, ...]) -> Tuple[story_types.Story, ...]:
  """Assemble a Story from it's component parts in DB

    Args:
        stories_in_db: The stories as they are in the 
          collection of the db.
    
    Returns:
      The stories with their associated Author, Source, and Entities
      in full objects instead of ids.

    """

  if not stories_in_db:
    return tuple()

  author_ids = set()
  source_ids = set()
  entity_links = set()
  keyword_texts = set()

  for story_in_db in stories_in_db:
    author_ids.add(story_in_db["author_id"])
    source_ids.add(story_in_db["source_id"])
    for entity_in_story_db in story_in_db["entities"]:
      entity_links.add(entity_in_story_db["links"])
    for keyword_in_story_db in story_in_db["keywords"]:
      keyword_texts.add(keyword_in_story_db["text"])

  authors = author.get_by_ids(tuple(author_ids))
  sources = source.get_by_ids(tuple(source_ids))
  entities = entity.get_by_links(tuple(entity_links))
  keywords = keyword.get_by_texts(tuple(keyword_texts),
                                  stories_in_db[0]["language"])

  stories = []
  for story_in_db in stories_in_db:
    story_dict = story_in_db
    story_dict.update({
        "author":
        next((author for author in authors
              if author.author_id == story_dict["author_id"]), None)
    })
    story_dict.update({
        "source":
        next((source for source in sources
              if source.source_id == story_dict["source_id"]), None)
    })
    entities_for_story = []
    for entity_in_story_db in story_dict["entities"]:
      found_entity = next((ent for ent in entities
                if ent.links == entity_in_story_db["links"]), None)
      if found_entity:
        entity_in_story_db.update({
            "entity": found_entity
        })
        entities_for_story.append(entity_in_story_db)
    story_dict["entities"] = entities_for_story
    keywords_for_story = []
    for keyword_in_story_db in story_dict["keywords"]:
      found_keyword = next((word for word in keywords
                if word.text == keyword_in_story_db["text"]), None)
      if found_keyword:
        keyword_in_story_db.update({
            "keyword": found_keyword
        })
        keywords_for_story.append(keyword_in_story_db)
    story_dict["keywords"] = keywords_for_story
    stories.append(story_types.Story(**story_dict))
  return tuple(stories)


def add_or_update_stories(stories: Tuple[story_types.Story, ...]):
  """Adds stories to the database with no checks. Use insert_stories() instead.

    Args:
        stories: The stories to store.

    Returns:
        The mongo result of the operation.

    """

  stories_to_push = tuple(
      story_types.convert_story_to_story_in_db(s).dict() for s in stories)
  return mongo.add_or_update(stories_to_push, DB_COLLECTION_NAME)


def get_by_id(story_id: str) -> Optional[story_types.Story]:
  """Retrieves the story from the database by id.

    Args:
        story_id: The id of the story.

    Returns:
        The story if found, otherwise None.

    """

  mongo_filter = {"story_id": UUID(story_id)}
  stories = mongo.get(DB_COLLECTION_NAME, mongo_filter)
  if stories:
    formatted_stories = build_stories_from_db(stories)
    if formatted_stories:
      return formatted_stories[0]
  return None


def update_feedback_counts(story_id: str, feedback_type: int):
  """Updates the feedback count by 1 for any given story and type of feedback.

    Args:
        story_id: The id of the story.
        feedback_type: the int which represent which feedback count to
          increment.

    Returns:
        The result of the mongo operation. If the story is not found it
        returns None.

    """

  mongo_filter = {"story_id": UUID(story_id)}
  stories = mongo.get(DB_COLLECTION_NAME, mongo_filter, limit=1)
  if stories:
    story = stories[0]
    if feedback_type == 0:
      story["read_count"] += 1
    if feedback_type == 1:
      story["shared_count"] += 1
    if feedback_type == 31:
      story["angry_count"] += 1
    if feedback_type == 32:
      story["cry_count"] += 1
    if feedback_type == 33:
      story["neutral_count"] += 1
    if feedback_type == 34:
      story["smile_count"] += 1
    if feedback_type == 35:
      story["happy_count"] += 1
    return mongo.add_or_update(story, DB_COLLECTION_NAME)
  return None


def get_public_stories(
    language: str = "en") -> Tuple[story_types.ShortStory, ...]:
  """Retrieves stories that are not using personalization, and that
  are to be viewed by anyone.

    Args:
        language: The language of the returned news stories

    Returns:
        A Tuple of news stories from the previous n days. Only one story
        per source is returned.

    """

  end = datetime.utcnow()
  delta = timedelta(days=PREVIOUS_DAYS_OF_NEWS)
  start = end - delta
  mongo_filter = {
      "language": language,
      "published_at": {
          "$gte": start,
          "$lt": end
      }
  }
  stories = mongo.get_grouped(DB_COLLECTION_NAME, mongo_filter, "source_id")
  formatted_stories = build_stories_from_db(stories)
  return tuple(
      story_types.convert_story_to_short_story(story)
      for story in formatted_stories)


def get_recommended_stories(user_id: str,
                            language: str = "en"
                            ) -> Tuple[story_types.ShortStory, ...]:
  """Retrieves stories that are recommended for a user.

    Args:
        user_id: Id of the user for whom to recommend stories to.
        language: The language of the returned news stories

    Returns:
        A Tuple of recommended news stories from the previous n days.
        Only one story per source is returned.
        Stories that have been previously read by the user are dismissed.
        If a user id is not provided generic stories are returned.

    """

  mongo_filter = {"language": language, "story_id": {}}
  if not user_id:
    return get_public_stories()
  read_story_ids = read_story.get_story_ids(user_id)
  not_id_list = tuple(UUID(i) for i in read_story_ids)
  if not_id_list:
    mongo_filter["story_id"].update({"$nin": not_id_list})
  response = requests.get(setup.get_base_ml_service_url() +
                          "/recommendations/" + user_id + "/" + language)
  if response:
    story_ids = list(response.json())
    is_id_list = tuple(UUID(i) for i in story_ids if i not in not_id_list)
    mongo_filter["story_id"].update({"$in": is_id_list})
    stories = mongo.get(DB_COLLECTION_NAME, mongo_filter, limit=12)
    formatted_stories = build_stories_from_db(stories)
    return tuple(
        story_types.convert_story_to_short_story(s) for s in formatted_stories)
  end = datetime.utcnow()
  delta = timedelta(days=PREVIOUS_DAYS_OF_NEWS)
  start = end - delta
  published_at = {"$gte": start, "$lt": end}
  mongo_filter.update({"published_at": published_at})
  stories = mongo.get_grouped(DB_COLLECTION_NAME, mongo_filter, "source_id")
  formatted_stories = build_stories_from_db(stories)
  return tuple(
      story_types.convert_story_to_short_story(s) for s in formatted_stories)


# Need to handle if personalization request
def get_single_story(not_id_list: List[str],
                     language: str) -> story_types.ShortStory:
  """Retrieves a single news story. This is used to return a story to
  the front-end after one has disappeared after having been rated.

    Args:
        not_id_list: A list of story ids which the new story has to not be.
        language: The language of the returned news story.

    Returns:
        A news story that is different from the id list provided.

    """

  end = datetime.utcnow()
  delta = timedelta(days=PREVIOUS_DAYS_OF_NEWS)
  start = end - delta
  mongo_filter = {
      "language": language,
      "published_at": {
          "$gte": start,
          "$lt": end
      },
      "story_id": {
          "$nin": tuple(UUID(i) for i in not_id_list)
      }
  }
  stories = mongo.get_grouped(DB_COLLECTION_NAME, mongo_filter, "source_id")
  formatted_stories = build_stories_from_db(stories)
  if formatted_stories:
    return story_types.convert_story_to_short_story(formatted_stories[0])
  return None


def update_tf_index(language: str) -> List[data_set_types.RankingData]:
  """Extracts the features from news stories of the previous n days,
  which are then packaged as Ranking Data for the updating of the tensor flow
  index used to return recommended stories. This needs to be done after every
  training cycle.

    Args:
        language: The language of the index that needs to be updated.

    Returns:
        A list of ranking data needed to update the tensor flow index.

    """

  end = datetime.utcnow()
  delta = timedelta(days=PREVIOUS_DAYS_OF_NEWS)
  start = end - delta
  mongo_filter = {
      "language": language,
      "published_at": {
          "$gte": start,
          "$lt": end
      }
  }
  ranking_data = []
  stories = mongo.get(DB_COLLECTION_NAME, mongo_filter)
  formatted_stories = build_stories_from_db(stories)
  for story in formatted_stories:
    if story:
      story_features = features.extract_ranking_features(story)
      data_entry = {"story_id": story.story_id}
      data_entry.update(story_features.dict())
      ranking_data.append(data_entry)
  return ranking_data
