from pytest_mock import MockerFixture
from unittest.mock import call

from services.user import favorite


def test_get_favorites(mocker: MockerFixture):
  spy = mocker.patch('services.user.favorite.mongo.get',
                     return_value=[mockFavorite().dict()])

  assert favorite.get_favorites("3d925894-7c07-4d70-be56-09f8e1f1071c",
                                "FavoriteSource", 10,
                                "en") == (mockFavorite(), )

  spy.assert_called_once_with("FavoriteSource", {
      "user_id": "3d925894-7c07-4d70-be56-09f8e1f1071c",
      "is_favorite": True,
      "is_deleted": False,
      "language": "en"
  },
                              limit=10,
                              sort="relevancy_rate",
                              reverse=True)


def test_get_recommended_favorites(mocker: MockerFixture):
  spy = mocker.patch('services.user.favorite.mongo.get', return_value=[])
  spy_grouped = mocker.patch('services.user.favorite.mongo.get_grouped',
                             return_value=[mockFavorite().dict()])

  mocked_favorite = mockFavorite()
  mocked_favorite.is_recommended = True
  mocked_favorite.is_favorite = False
  mocked_favorite.is_added = False
  assert favorite.get_recommended_favorites(
      "3d925894-7c07-4d70-be56-09f8e1f1071c", "FavoriteSource", 10,
      "en") == (mocked_favorite, )

  spy.assert_called_once_with("FavoriteSource", {
      "user_id": "3d925894-7c07-4d70-be56-09f8e1f1071c",
      "is_deleted": True,
      "language": "en"
  },
                              limit=10,
                              sort="relevancy_rate",
                              reverse=True)

  spy_grouped.assert_called_once_with("FavoriteSource", {
      "is_deleted": False,
      "language": "en"
  },
                                      "identifier",
                                      limit=10,
                                      sort="relevancy_rate",
                                      reverse=True)


def test_get_favorite_items(mocker: MockerFixture):
  spy = mocker.patch('services.user.favorite.get_favorites',
                     return_value=[mockFavorite()])

  assert favorite.get_favorite_items("3d925894-7c07-4d70-be56-09f8e1f1071c",
                                     10, "en") == mock_favorite_items()

  spy.has_calls([
      call("3d925894-7c07-4d70-be56-09f8e1f1071c", "FavoriteEntity", 10, "en"),
      call("3d925894-7c07-4d70-be56-09f8e1f1071c", "FavoriteKeyword", 10,
           "en"),
      call("3d925894-7c07-4d70-be56-09f8e1f1071c", "FavoriteAuthor", 10, "en"),
      call("3d925894-7c07-4d70-be56-09f8e1f1071c", "FavoriteSource", 10, "en")
  ])


def test_get_recommended_favorite_items(mocker: MockerFixture):
  spy = mocker.patch('services.user.favorite.get_recommended_favorites',
                     return_value=[mockFavorite()])

  assert favorite.get_recommended_favorite_items(
      "3d925894-7c07-4d70-be56-09f8e1f1071c", 10,
      "en") == mock_favorite_items()

  spy.has_calls([
      call("3d925894-7c07-4d70-be56-09f8e1f1071c", "FavoriteEntity", 10, "en"),
      call("3d925894-7c07-4d70-be56-09f8e1f1071c", "FavoriteKeyword", 10,
           "en"),
      call("3d925894-7c07-4d70-be56-09f8e1f1071c", "FavoriteAuthor", 10, "en"),
      call("3d925894-7c07-4d70-be56-09f8e1f1071c", "FavoriteSource", 10, "en")
  ])


def test_update_from_user(mocker: MockerFixture):
  spy = mocker.patch('services.user.favorite.mongo.add_or_update',
                     return_value=True)

  assert favorite.update_from_user(mockFavorite(), "FavoriteSource") == True

  spy.assert_called_once_with(mockFavorite().dict(), "FavoriteSource")


def test_update_from_story(mocker: MockerFixture):
  spy_get = mocker.patch('services.user.favorite.mongo.get',
                         return_value=[mockFavorite().dict()])
  spy_set = mocker.patch('services.user.favorite.mongo.add_or_update',
                         return_value=True)

  assert favorite.update_from_story("3d925894-7c07-4d70-be56-09f8e1f1071c",
                                    "shell", "shell", 1.0, "FavoriteSource",
                                    "en") == True

  spy_get.assert_called_once_with("FavoriteSource", {
      "user_id": mockFavorite().user_id,
      "identifier": mockFavorite().identifier
  })
  mocked_favorite = mockFavorite()
  mocked_favorite.relevancy_rate = 1.0
  spy_set.assert_called_once_with(mocked_favorite.dict(), "FavoriteSource")


def mock_favorite_items() -> favorite.FavoriteItems:
  return favorite.FavoriteItems(favorite_sources=[mockFavorite()],
                                favorite_authors=[mockFavorite()],
                                favorite_keywords=[mockFavorite()],
                                favorite_entities=[mockFavorite()])


def mockFavorite() -> favorite.Favorite:
  return favorite.Favorite(id="029183012978312",
                           user_id="3d925894-7c07-4d70-be56-09f8e1f1071c",
                           identifier="shell",
                           value="shell",
                           is_favorite=False,
                           is_deleted=False,
                           is_recommended=False,
                           is_added=False,
                           relevancy_rate=0.0,
                           language="en")
