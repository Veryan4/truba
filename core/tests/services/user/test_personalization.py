from pytest_mock import MockerFixture
import pytest
from unittest.mock import call
from services.user import personalization
from tests.services.user.test_favorite import mock_favorite_items
from tests.services.user.test_user import mock_user


def test_get_personalization(mocker: MockerFixture):
  spy_recommended = mocker.patch(
      'services.user.personalization.favorite.get_recommended_favorite_items',
      return_value=mock_favorite_items())
  spy_favorite = mocker.patch(
      'services.user.personalization.favorite.get_favorite_items',
      return_value=mock_favorite_items())
  spy_hated = mocker.patch(
      'services.user.personalization.favorite.get_hated_items',
      return_value=mock_favorite_items())

  assert personalization.get_personalization(mock_user().user_id,
                                             "en") == mock_Personalization()

  spy_recommended.assert_called_once_with(mock_user().user_id, 10, "en")
  spy_favorite.assert_called_once_with(mock_user().user_id, 10, "en")
  spy_hated.assert_called_once_with(mock_user().user_id, 10, "en")


def test_add_solr_model(requests_mock, mocker: MockerFixture):
  mocker.patch('services.user.personalization.setup.get_base_ml_service_url',
               return_value="http://ml:8080")
  requests_mock.get("http://ml:8080/model-store/" + mock_user().user_id,
                    text='OK')

  assert personalization.add_solr_model(mock_user().user_id).text == 'OK'


def test_compare_favorites(mocker: MockerFixture):
  assert personalization.compare_favorites(['hello', 'goodbye'],
                                           ['hello', 'goodbye']) == 1.0
  assert personalization.compare_favorites(['hello', 'goodbye'],
                                           ['hello']) == 0.5
  assert pytest.approx(
      personalization.compare_favorites(['hello', 'goodbye'],
                                        ['hello', 'orange']), 0.1) == 0.3
  assert personalization.compare_favorites(['hello', 'goodbye'],
                                           ['blue', 'orange']) == 0.0


def test_find_most_similar_profile(mocker: MockerFixture):
  spy_ids = mocker.patch('services.user.personalization.user.get_ids',
                         return_value=[mock_user().user_id])
  spy_favorite = mocker.patch(
      'services.user.personalization.favorite.get_favorite_items',
      return_value=mock_favorite_items())
  spy_compare = mocker.patch('services.user.personalization.compare_favorites',
                             return_value=0.5)

  assert personalization.find_most_similar_profile(
      mock_favorite_items()) == mock_user().user_id

  spy_ids.assert_called_once()
  spy_favorite.assert_called_once_with(mock_user().user_id, 5)
  spy_compare.has_calls([
      call(mock_favorite_items(), mock_favorite_items()),
      call(mock_favorite_items(), mock_favorite_items()),
      call(mock_favorite_items(), mock_favorite_items()),
      call(mock_favorite_items(), mock_favorite_items())
  ])


def mock_Personalization() -> personalization.Personalization:
  return personalization.Personalization(
      recommended_items=mock_favorite_items(),
      favorite_items=mock_favorite_items(),
      hated_items=mock_favorite_items())
