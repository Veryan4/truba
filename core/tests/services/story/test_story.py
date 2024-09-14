from pytest_mock import MockerFixture
from datetime import datetime
from freezegun import freeze_time

from services.story import story
from tests import mocks
import project_types
from tests.services.search.test_features import mock_ranking_features


def test_insert_stories(mocker: MockerFixture):
  spy_author = mocker.patch('services.story.story.author.add_new_authors')
  spy_entity = mocker.patch('services.story.story.entity.add_new_entities')
  spy_keyword = mocker.patch('services.story.story.keyword.add_new_keywords')
  spy_story = mocker.patch('services.story.story.add_or_update_stories')
  spy_delete_story = mocker.patch('services.story.story.remove_old_stories')

  story.insert_stories((mocks.mock_story(), ))

  spy_author.assert_called_once_with((mocks.mock_author(), ))
  spy_entity.assert_called_once_with(
      tuple(ent.entity for ent in mocks.mock_story().entities))
  spy_keyword.assert_called_once_with(
      tuple(word.keyword for word in mocks.mock_story().keywords))
  spy_story.assert_called_with((mocks.mock_story(), ))
  spy_delete_story.assert_called_once()


@freeze_time("2021-01-04")
def test_remove_old_stories(mocker: MockerFixture):
  spy = mocker.patch('services.story.story.mongo.remove')

  story.remove_old_stories()

  spy.assert_called_once_with(
      "Story", {"published_at": {
          '$lte': datetime(2020, 10, 6, 0, 0)
      }})


def test_add_or_update_stories(mocker: MockerFixture):
  spy = mocker.patch('services.story.story.mongo.add_or_update',
                     return_value=True)
  spy_converter = mocker.patch(
      'services.story.story.convert_story_to_story_in_db',
      return_value=mock_story_in_db())

  assert story.add_or_update_stories((mocks.mock_story(), )) == True

  spy_converter.assert_called_with(mocks.mock_story())
  spy.assert_called_with((mock_story_in_db().dict(), ), "Story")


def test_get_by_id(mocker: MockerFixture):
  spy = mocker.patch('services.story.story.mongo.get',
                     return_value=[mock_story_in_db().dict()])
  spy_builder = mocker.patch('services.story.story.build_stories_from_db',
                             return_value=[mocks.mock_story()])

  assert story.get_by_id(str(
      mocks.mock_story().story_id, )) == mocks.mock_story()

  spy.assert_called_once_with("Story",
                              {"story_id": mocks.mock_story().story_id})
  spy_builder.assert_called_once_with([mock_story_in_db().dict()])


def test_update_feedback_counts(mocker: MockerFixture):
  spy_get = mocker.patch('services.story.story.mongo.get',
                         return_value=[mock_story_in_db().dict()])
  spy_set = mocker.patch('services.story.story.mongo.add_or_update',
                         return_value=True)

  assert story.update_feedback_counts(str(mocks.mock_story().story_id),
                                      'shared') == True

  spy_get.assert_called_once_with(
      "Story", {"story_id": mocks.mock_story().story_id}, limit=1)
  current_story = mock_story_in_db().dict()
  current_story["shared_count"] += 1
  spy_set.assert_called_once_with(current_story, "Story")


@freeze_time("2021-01-04")
def test_get_public_stories(mocker: MockerFixture):
  spy = mocker.patch('services.story.story.mongo.get_grouped',
                     return_value=[mock_story_in_db().dict()])
  spy_builder = mocker.patch('services.story.story.build_stories_from_db',
                             return_value=[mocks.mock_story()])

  assert story.get_public_stories("en") == (
      story.convert_story_to_short_story(mocks.mock_story()), )

  spy.assert_called_once_with(
      "Story", {
          "language": "en",
          "published_at": {
              '$gte': datetime(2021, 1, 3, 0, 0, 0, 0),
              '$lt': datetime(2021, 1, 4, 0, 0, 0, 0)
          }
      }, "source_id")
  spy_builder.assert_called_once_with([mock_story_in_db().dict()])


class Testget_recommended_stories:
  user_id = str(mocks.mock_story().story_id)

  def test_hasRecommendedStories(self, requests_mock, mocker: MockerFixture):
    spy_read = mocker.patch('services.story.story.read_story.get_story_ids',
                            return_value=[])
    mocker.patch('services.story.story.UUID',
                 return_value=mocks.mock_story().story_id)
    mocker.patch('services.story.story.setup.get_base_ml_service_url',
                 return_value="http://ml:8080")
    requests_mock.get("http://ml:8080/recommendations/" + self.user_id + "/en",
                      json=[mocks.mock_story().json()])

    spy_get = mocker.patch('services.story.story.mongo.get',
                           return_value=[mock_story_in_db().dict()])
    spy_builder = mocker.patch('services.story.story.build_stories_from_db',
                               return_value=[mocks.mock_story()])

    assert story.get_recommended_stories(
        self.user_id, "en") == (story.convert_story_to_short_story(
            mocks.mock_story()), )

    spy_read.assert_called_once_with(self.user_id)

    spy_get.assert_called_once_with("Story", {
        "language": "en",
        "story_id": {
            "$in": (mocks.mock_story().story_id, )
        }
    },
                                    limit=12)
    spy_builder.assert_called_once_with([mock_story_in_db().dict()])

  @freeze_time("2021-01-04")
  def test_NoRecommendedStories(self, requests_mock, mocker: MockerFixture):
    spy_read = mocker.patch('services.story.story.read_story.get_story_ids',
                            return_value=[])
    mocker.patch('services.story.story.UUID',
                 return_value=mocks.mock_story().story_id)
    mocker.patch('services.story.story.setup.get_base_ml_service_url',
                 return_value="http://ml:8080")
    requests_mock.get("http://ml:8080/recommendations/" + self.user_id + "/en",
                      json=[],
                      status_code=404)
    spy_get_grouped = mocker.patch('services.story.story.mongo.get_grouped',
                                   return_value=[mock_story_in_db().dict()])
    spy_builder = mocker.patch('services.story.story.build_stories_from_db',
                               return_value=[mocks.mock_story()])

    assert story.get_recommended_stories(
        self.user_id, "en") == (story.convert_story_to_short_story(
            mocks.mock_story()), )

    spy_read.assert_called_once_with(self.user_id)
    spy_get_grouped.assert_called_once_with(
        "Story", {
            "language": "en",
            "story_id": {},
            "published_at": {
                '$gte': datetime(2021, 1, 3, 0, 0, 0, 0),
                '$lt': datetime(2021, 1, 4, 0, 0, 0, 0)
            }
        }, "source_id")
    spy_builder.assert_called_once_with([mock_story_in_db().dict()])


@freeze_time("2021-01-04")
def test_get_single_story(mocker: MockerFixture):
  mocker.patch('services.story.story.UUID',
               return_value=mocks.mock_story().story_id)
  spy_get_grouped = mocker.patch('services.story.story.mongo.get_grouped',
                                 return_value=[mock_story_in_db().dict()])
  spy_builder = mocker.patch('services.story.story.build_stories_from_db',
                             return_value=[mocks.mock_story()])

  assert story.get_single_story(
      [str(mocks.mock_story().story_id)],
      "en") == story.convert_story_to_short_story(
          mocks.mock_story())

  spy_builder.assert_called_once_with([mock_story_in_db().dict()])
  spy_get_grouped.assert_called_once_with(
      "Story", {
          "language": "en",
          "published_at": {
              '$gte': datetime(2021, 1, 3, 0, 0, 0, 0),
              '$lt': datetime(2021, 1, 4, 0, 0, 0, 0)
          },
          "story_id": {
              "$nin": (mocks.mock_story().story_id, )
          }
      }, "source_id")


@freeze_time("2021-01-04")
def test_update_tf_index(mocker: MockerFixture):
  spy_get = mocker.patch('services.story.story.mongo.get',
                         return_value=[mock_story_in_db().dict()])
  spy_builder = mocker.patch('services.story.story.build_stories_from_db',
                             return_value=[mocks.mock_story()])
  spy_ranking_features = mocker.patch(
      'services.story.story.features.extract_ranking_features',
      return_value=mock_ranking_features())

  assert story.update_tf_index("en") == [mock_ranking_data()]

  spy_builder.assert_called_once_with([mock_story_in_db().dict()])
  spy_ranking_features.assert_called_once_with(mocks.mock_story())
  spy_get.assert_called_once_with(
      "Story", {
          "language": "en",
          "published_at": {
              '$gte': datetime(2021, 1, 3, 0, 0, 0, 0),
              '$lt': datetime(2021, 1, 4, 0, 0, 0, 0)
          }
      })


def mock_ranking_data() -> project_types.RankingData:
    mock_story = mocks.mock_story()
    return {
        "story_id": mock_story.story_id,
        "story_title": mock_story.title,
        "source_alexa_rank": 1048,
        "read_count": 0,
        "shared_count": 0,
        "angry_count": 0,
        "cry_count": 0,
        "neutral_count": 0,
        "smile_count": 0,
        "happy_count": 0,
        "source_id": str(mock_story.source.source_id),
        "author_id": str(mock_story.author.author_id),
        "most_frequent_keyword": "Apple",
        "most_frequent_entity": "AppleORG"
    }


def mock_story_in_db() -> project_types.StoryInDb:
  mocked_story = mocks.mock_story()
  return project_types.StoryInDb(
      id="",
      story_id=mocked_story.story_id,
      title=mocked_story.title,
      body=mocked_story.body,
      summary=mocked_story.summary,
      source_id=mocked_story.source.source_id,
      author_id=mocked_story.author.author_id,
      entities=[{"links": ent.entity.links, "frequency": 0} for ent in mocked_story.entities],
      keywords=[{"text": k.keyword.text, "frequency": 0} for k in mocked_story.keywords],
      images=mocked_story.images,
      language=mocked_story.language,
      published_at=mocked_story.published_at,
      url=mocked_story.url,
      read_count=mocked_story.read_count,
      shared_count=mocked_story.shared_count,
      angry_count=mocked_story.angry_count,
      cry_count=mocked_story.cry_count,
      neutral_count=mocked_story.neutral_count,
      smile_count=mocked_story.smile_count,
      happy_count=mocked_story.happy_count)
