from pytest_mock import MockerFixture
from datetime import datetime
from freezegun import freeze_time

from services.user import read_story


def test_add(mocker: MockerFixture):
  spy = mocker.patch('services.user.read_story.mongo.add_or_update',
                     return_value=True)

  assert read_story.add(mockReadStory()) == True

  spy.assert_called_once_with(mockReadStory().dict(), "ReadStory")


@freeze_time("2021-01-04")
def test_get_story_ids(mocker: MockerFixture):
  spy = mocker.patch('services.user.read_story.mongo.get',
                     return_value=[mockReadStory().dict()])

  assert read_story.get_story_ids(
      mockReadStory().user_id) == (mockReadStory().story_id, )

  spy.assert_called_once_with(
      "ReadStory", {
          "user_id": mockReadStory().user_id,
          "read_time": {
              '$gte': datetime(2021, 1, 3, 0, 0, 0, 0),
              '$lt': datetime(2021, 1, 4, 0, 0, 0, 0)
          }
      })


def mockReadStory() -> read_story.ReadStory:
  return read_story.ReadStory(user_id="3d925894-7c07-4d70-be56-09f8e1f1071c",
                              story_id="3d925894-7c07-4d70-be56-09f8e1f1071c",
                              read_time=datetime(2021, 1, 4, 0, 0, 0, 0))
