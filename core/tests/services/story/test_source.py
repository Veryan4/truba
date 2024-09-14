from pytest_mock import MockerFixture

from services.story import source
from tests import mocks


def test_add_new_sources(mocker: MockerFixture):
  spy_get = mocker.patch('services.story.source.mongo.get', return_value=[])
  spy_set = mocker.patch('services.story.source.mongo.add_or_update',
                         return_value=True)

  assert source.add_new_sources((mocks.mock_source(), )) == True

  spy_get.assert_called_once_with(
      "Source", {"name": {
          "$in": (mocks.mock_source().name, )
      }})
  spy_set.assert_called_once_with((mocks.mock_source().dict(), ),
                                  "Source")


def test_get_by_name(mocker: MockerFixture):
  spy = mocker.patch('services.story.source.mongo.get',
                     return_value=[mocks.mock_source().dict()])

  assert source.get_by_name("BBC") == mocks.mock_source()

  spy.assert_called_once_with("Source", {"name": "BBC"}, limit=1)


def test_get_by_id(mocker: MockerFixture):
  spy = mocker.patch('services.story.source.mongo.get',
                     return_value=[mocks.mock_source().dict()])

  assert source.get_by_id(str(
      mocks.mock_source().source_id)) == mocks.mock_source()

  spy.assert_called_once_with(
      "Source", {"source_id": mocks.mock_source().source_id}, limit=1)


def test_get_source_name(mocker: MockerFixture):
  spy = mocker.patch('services.story.source.mongo.get',
                     return_value=[mocks.mock_source().dict()])

  assert source.get_source_name(str(
      mocks.mock_source().source_id)) == mocks.mock_source().name

  spy.assert_called_once_with(
      "Source", {"source_id": mocks.mock_source().source_id}, limit=1)


def test_get_all_sources(mocker: MockerFixture):
  spy = mocker.patch('services.story.source.mongo.get',
                     return_value=[mocks.mock_source().dict()])

  assert source.get_all_sources("en") == (mocks.mock_source(), )

  spy.assert_called_once_with("Source", {"language": "en"})


def test_reset_sources(mocker: MockerFixture):
  spy_remove = mocker.patch('services.story.source.mongo.remove')
  mocker.patch('services.story.source.open')
  spy_set = mocker.patch(
      'services.story.source.json.load',
      return_value={"sources": (mocks.mock_source().dict(), )})
  spy_set = mocker.patch('services.story.source.mongo.add_or_update',
                         return_value=True)

  assert source.reset_sources() == True

  spy_remove.assert_called_once_with("Source", {})
  spy_set.assert_called_once_with((mocks.mock_source().dict(), ),
                                  "Source")


def test_update_reputation(mocker: MockerFixture):
  spy_get = mocker.patch('services.story.source.mongo.get',
                         return_value=[mocks.mock_source().dict()])
  spy_set = mocker.patch('services.story.source.mongo.add_or_update',
                         return_value=True)

  assert source.update_reputation(str(mocks.mock_source().source_id),
                                  0.1) == True

  spy_get.assert_called_once_with(
      "Source", {"source_id": mocks.mock_source().source_id}, limit=1)
  mock_source = mocks.mock_source()
  mock_source.reputation = 0.1
  spy_set.assert_called_once_with(mock_source.dict(), "Source")
