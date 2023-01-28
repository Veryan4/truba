from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Tuple

from services.search import features
from services.story import story, source, author
from services.user import favorite, read_story
from services import mongo
from shared import bson_id
from shared.types import data_set_types

DB_COLLECTION_NAME = "UserFeedback"
USER_FEEDBACK_COUNT = 200
RANKING_DATA_FAVORITE_COUNT = 50
FEEDBACK_RECEIVED_REWARD = 0.1
URL_CLICKED_SCORE = 1.0
SHARED_SCORE = 5.0
ANGRY_SCORE = -5.0
CRY_SCORE = -2.0
NEUTRAL_SCORE = 0.0
SMILE_SCORE = 2.0
HAPPY_SCORE = 5.0


class UserFeedback(BaseModel):
  id: bson_id.ObjectIdStr = Field(None, alias='_id')
  user_id: str
  story_id: str
  search_term: str = "*"
  feedback_datetime: datetime = Field(default_factory=datetime.utcnow)
  feedback_type: int


def add(user_feedback: UserFeedback):
  """Straight adding of a UserFeedback object to Mongo.

    Args:
        user_feedback: The user's feedback to be added to Mongo.

    Returns:
        The results of the mongo operation.

    """

  return mongo.add_or_update(user_feedback.dict(), DB_COLLECTION_NAME)


def remove_feedback_of_user(user_id: str):
  """Remove all feedbacks for a given user from Mongo.

    Args:
        user_id: The user id for which to remove the feedback.

    Returns:
        The amount of user feedbacks deleted.

    """

  mongo_filter = {"user_id": user_id}
  r = mongo.remove(DB_COLLECTION_NAME, mongo_filter)
  return r.deleted_count


def get_list(user_id: str) -> Tuple[UserFeedback, ...]:
  """Retrieve a list of feedbacks from a user

    Args:
        user_id: The user id for which to remove the feedback.

    Returns:
        A tuple of user feedbacks.

    """

  mongo_filter = {}
  if user_id != 'defaultmodel':
    mongo_filter.update({"user_id": user_id})
  feedbacks = mongo.get(DB_COLLECTION_NAME,
                        mongo_filter,
                        limit=USER_FEEDBACK_COUNT,
                        sort="feedback_datetime",
                        reverse=True)
  return tuple(UserFeedback(**feedback) for feedback in feedbacks)


def convert_feedback_type_to_relevancy_rate(feedback_type: int) -> float:
  if feedback_type == 0:
    return URL_CLICKED_SCORE
  elif feedback_type == 1:
    return SHARED_SCORE
  elif feedback_type == 31:
    return ANGRY_SCORE
  elif feedback_type == 32:
    return CRY_SCORE
  elif feedback_type == 33:
    return NEUTRAL_SCORE
  elif feedback_type == 34:
    return SMILE_SCORE
  elif feedback_type == 35:
    return HAPPY_SCORE


def get_tf_training_data(user_id: str) -> List[data_set_types.RankingData]:
  """Retrieves a list of tensorflow training data generated from the user
  feedback.

    Args:
        user_id: The user id for which to retrieve the training data.

    Returns:
        A list of tensorflow training data.

    """

  feedback_list = get_list(user_id)
  data_entry_list = []
  relevancy_dict = {}
  time_dict = {}
  for feedback in feedback_list:
    relevancy_rate = convert_feedback_type_to_relevancy_rate(
        feedback.feedback_type)
    if feedback.story_id in relevancy_dict:
      relevancy_dict[feedback.story_id] += relevancy_rate
    else:
      relevancy_dict.update({feedback.story_id: relevancy_rate})
    if feedback.story_id in time_dict:
      if feedback.feedback_datetime > time_dict[feedback.story_id]:
        time_dict.update({feedback.story_id: feedback.feedback_datetime})
    else:
      time_dict.update({feedback.story_id: feedback.feedback_datetime})
  for story_id in relevancy_dict.keys():
    current_story = story.get_by_id(story_id)
    if current_story:
      ranking_features = features.extract_ranking_features(current_story)
      if ranking_features:
        data_entry = {
            "story_id": story_id,
            "user_id": user_id,
            "relevancy_rate": relevancy_dict[story_id],
            "time_stamp": datetime.timestamp(time_dict[story_id])
        }
        data_entry.update(ranking_features.dict())
        data_entry_list.append(data_set_types.RankingData(**data_entry))
  return data_entry_list


def received(feedback: UserFeedback):
  """Updates relevant values after receiving feedback on a news story from a
  user. Stories which have been read by the user are accounted for and the
  relevancy rate of the user's favorites are updated. The overall reputation
  of the source and author are also updated.

    Args:
        feedback: The feedback received from the User.

    Returns:
        The result of adding the feedback to mongo.

    """

  current_read_story = read_story.ReadStory(story_id=feedback.story_id,
                                            user_id=feedback.user_id)
  read_story.add(current_read_story)
  result = add(feedback)
  reward = None
  #Angry
  if feedback.feedback_type == 31:
    reward = -FEEDBACK_RECEIVED_REWARD
  #Happy or Shared
  elif feedback.feedback_type == 35 or feedback.feedback_type == 1:
    reward = FEEDBACK_RECEIVED_REWARD
  current_story = story.get_by_id(feedback.story_id)
  if current_story:
    story.update_feedback_counts(feedback.story_id, feedback.feedback_type)
    if reward:
      if current_story.keywords:
        for keyword in current_story.keywords:
          favorite.update_from_story(
              feedback.user_id,
              keyword.keyword.text,
              keyword.keyword.text,
              reward,
              favorite.FAVORITE_KEYWORD_DB_COLLECTION_NAME,
              language=current_story.language)
      if current_story.entities:
        for e in current_story.entities:
          favorite.update_from_story(
              feedback.user_id,
              e.entity.links,
              e.entity.text,
              reward,
              favorite.FAVORITE_ENTITY_DB_COLLECTION_NAME,
              language=current_story.language)
      if current_story.source:
        favorite.update_from_story(feedback.user_id,
                                   current_story.source.source_id,
                                   current_story.source.name,
                                   reward,
                                   favorite.FAVORITE_SOURCE_DB_COLLECTION_NAME,
                                   language=current_story.language)
        source.update_reputation(current_story.source.source_id, reward)
      if current_story.author:
        favorite.update_from_story(feedback.user_id,
                                   current_story.author.author_id,
                                   current_story.author.name,
                                   reward,
                                   favorite.FAVORITE_AUTHOR_DB_COLLECTION_NAME,
                                   language=current_story.language)
        author.update_reputation(current_story.author.author_id, reward)
  return result
