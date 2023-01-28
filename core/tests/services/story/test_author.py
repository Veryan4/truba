from pytest_mock import MockerFixture

from services.story import author
from shared.types import author_types


def test_add_new_authors(mocker: MockerFixture):
  spy_get = mocker.patch('services.story.author.mongo.get', return_value=[])
  spy_set = mocker.patch('services.story.author.mongo.add_or_update',
                         return_value=True)

  assert author.add_new_authors((author_types.mock_author(), )) == True

  spy_get.assert_called_once_with(
      "Author",
      {"author_id": {
          "$in": (author_types.mock_author().author_id, )
      }})
  spy_set.assert_called_once_with((author_types.mock_author().dict(), ),
                                  "Author")


def test_get_by_name(mocker: MockerFixture):
  spy = mocker.patch('services.story.author.mongo.get',
                     return_value=[author_types.mock_author().dict()])

  assert author.get_by_name("Tom Lundy") == author_types.mock_author()

  spy.assert_called_once_with("Author", {"name": "Tom Lundy"}, limit=1)


def test_get_by_id(mocker: MockerFixture):
  spy = mocker.patch('services.story.author.mongo.get',
                     return_value=[author_types.mock_author().dict()])

  assert author.get_by_id(str(
      author_types.mock_author().author_id)) == author_types.mock_author()

  spy.assert_called_once_with(
      "Author", {"author_id": author_types.mock_author().author_id}, limit=1)


def test_update_reputation(mocker: MockerFixture):
  spy_get = mocker.patch('services.story.author.mongo.get',
                         return_value=[author_types.mock_author().dict()])
  spy_set = mocker.patch('services.story.author.mongo.add_or_update',
                         return_value=True)

  assert author.update_reputation(str(author_types.mock_author().author_id),
                                  0.1) == True

  spy_get.assert_called_once_with(
      "Author", {"author_id": author_types.mock_author().author_id}, limit=1)
  mock_author = author_types.mock_author()
  mock_author.reputation = 0.1
  spy_set.assert_called_once_with(mock_author.dict(), "Author")
