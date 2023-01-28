from pytest_mock import MockerFixture
from unittest.mock import call
from datetime import datetime
from freezegun import freeze_time

from services.user import feedback
from shared.types import data_set_types, story_types
from tests.services.search.test_features import mock_ranking_features


def test_add(mocker: MockerFixture):
  spy = mocker.patch('services.user.feedback.mongo.add_or_update',
                     return_value=True)

  assert feedback.add(mock_user_feedback()) == True

  spy.assert_called_once_with(mock_user_feedback().dict(), "UserFeedback")


def test_remove_feedback_of_user(mocker: MockerFixture):
  spy = mocker.patch('services.user.feedback.mongo.remove')

  feedback.remove_feedback_of_user(mock_user_feedback().user_id)

  spy.assert_called_once_with("UserFeedback",
                              {"user_id": mock_user_feedback().user_id})


@freeze_time("2021-02-04")
def test_get_list(mocker: MockerFixture):
  spy = mocker.patch('services.user.feedback.mongo.get',
                     return_value=[mock_user_feedback().dict()])

  assert feedback.get_list(
      mock_user_feedback().user_id) == (mock_user_feedback(), )

  spy.assert_called_once_with("UserFeedback", {
      "user_id": mock_user_feedback().user_id,
  },
                              limit=200, sort="feedback_datetime", reverse=True)


def test_convert_feedback_type_to_relevancy_rate(mocker: MockerFixture):
  assert feedback.convert_feedback_type_to_relevancy_rate(0) == 1.0
  assert feedback.convert_feedback_type_to_relevancy_rate(1) == 5.0
  assert feedback.convert_feedback_type_to_relevancy_rate(31) == -5.0
  assert feedback.convert_feedback_type_to_relevancy_rate(32) == -2.0
  assert feedback.convert_feedback_type_to_relevancy_rate(33) == 0.0
  assert feedback.convert_feedback_type_to_relevancy_rate(34) == 2.0
  assert feedback.convert_feedback_type_to_relevancy_rate(35) == 5.0


@freeze_time("2021-01-04")
def test_get_tf_training_data(mocker: MockerFixture):
  spy_get = mocker.patch('services.user.feedback.get_list',
                         return_value=[mock_user_feedback()])
  spy_covert = mocker.patch(
      'services.user.feedback.convert_feedback_type_to_relevancy_rate',
      return_value=5.0)
  spy_story = mocker.patch('services.user.feedback.story.get_by_id',
                           return_value=story_types.mock_story())
  spy_feature = mocker.patch(
      'services.user.feedback.features.extract_ranking_features',
      return_value=mock_ranking_features())

  ranking_data = mock_ranking_data()
  ranking_data.relevancy_rate = 5.0
  assert feedback.get_tf_training_data(
      mock_user_feedback().user_id) == [ranking_data]

  spy_get.assert_called_once_with(mock_user_feedback().user_id)
  spy_covert.assert_called_once_with(1)
  spy_story.assert_called_once_with(str(story_types.mock_story().story_id))
  spy_feature.assert_called_once_with(story_types.mock_story())


@freeze_time("2021-01-04")
def test_received(mocker: MockerFixture):
  mocker.patch('services.user.feedback.read_story.add')
  spy_add = mocker.patch('services.user.feedback.add', return_value=True)
  spy_story = mocker.patch('services.user.feedback.story.get_by_id',
                           return_value=story_types.mock_story())
  spy_feedback = mocker.patch(
      'services.user.feedback.story.update_feedback_counts')
  spy_favorite = mocker.patch(
      'services.user.feedback.favorite.update_from_story')
  spy_author = mocker.patch('services.user.feedback.author.update_reputation')
  spy_source = mocker.patch('services.user.feedback.source.update_reputation')

  assert feedback.received(mock_user_feedback()) == True

  spy_add.assert_called_once_with(mock_user_feedback())
  spy_story.assert_called_once_with(str(story_types.mock_story().story_id))
  spy_feedback.assert_called_once_with(mock_user_feedback().story_id,
                                       mock_user_feedback().feedback_type)
  spy_favorite.has_calls([
      call(mock_user_feedback().user_id,
           story_types.mock_story().keywords[0].keyword.text,
           story_types.mock_story().keywords[0].keyword.text,
           0.1,
           "FavoriteKeyword",
           language="en"),
      call(mock_user_feedback().user_id,
           story_types.mock_story().entities[0].entity.links,
           story_types.mock_story().entities[0].entity.text,
           0.1,
           "FavoriteEntity",
           language="en"),
      call(mock_user_feedback().user_id,
           story_types.mock_story().source.source_id,
           story_types.mock_story().source.name,
           0.1,
           "FavoriteSource",
           language="en"),
      call(mock_user_feedback().user_id,
           story_types.mock_story().author.author_id,
           story_types.mock_story().author.name,
           0.1,
           "FavoriteAuthor",
           language="en"),
  ])
  spy_author.assert_called_once_with(story_types.mock_story().author.author_id,
                                     0.1)
  spy_source.assert_called_once_with(story_types.mock_story().source.source_id,
                                     0.1)


def mock_user_feedback() -> feedback.UserFeedback:
  return feedback.UserFeedback(id="",
                               user_id="3d925894-7c07-4d70-be56-09f8e1f1071c",
                               story_id="3d925894-7c07-4d70-be56-09f8e1f1071c",
                               search_term="*",
                               feedback_datetime=datetime(
                                   2021, 1, 4, 0, 0, 0, 0),
                               feedback_type=1)


def mock_ranking_data() -> data_set_types.RankingData:
    mock_story = story_types.mock_story()
    return data_set_types.RankingData(story_id=mock_user_feedback().story_id,
                                    user_id=mock_user_feedback().user_id,
                                    story_title=mock_story.title,
                                    time_stamp=datetime.timestamp(
                                        datetime(2021, 1, 4, 0, 0, 0, 0)),
                                    source_alexa_rank=1048,
                                    read_count=0,
                                    shared_count=0,
                                    angry_count=0,
                                    cry_count=0,
                                    neutral_count=0,
                                    smile_count=0,
                                    happy_count=0,
                                    source_id=str(mock_story.source.source_id),
                                    author_id=str(mock_story.author.author_id),
                                    most_frequent_keyword="Apple",
                                    most_frequent_entity="AppleORG")
