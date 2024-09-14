from pytest_mock import MockerFixture
import pytest
from datetime import datetime
from freezegun import freeze_time
from fastapi.encoders import jsonable_encoder

from services import scraper
import project_types
from tests import mocks


@pytest.fixture(autouse=True)  #before each
def run_around_tests(mocker: MockerFixture):
  mocker.patch('services.scraper.tracing.log')
  mocker.patch('shared.setup.get_base_core_service_url',
               return_value="http://127.0.0.1:5057")
  yield


def test_get_sources(requests_mock, mocker: MockerFixture):
  mocker.patch('os.getenv', return_value="en")
  requests_mock.get("http://127.0.0.1:5057/sources/en",
                    json=jsonable_encoder([mocks.mock_story().source]))

  assert scraper.get_sources() == (mocks.mock_story().source, )


def test_push_stories_to_core(requests_mock, mocker: MockerFixture):
  spyStories = requests_mock.post("http://127.0.0.1:5057/stories")
  spyScrapedUrl = requests_mock.post("http://127.0.0.1:5057/scraped")

  scraper.push_stories_to_core(mocks.mock_story().source,
                               [mocks.mock_story()])

  assert spyStories.called == True
  assert spyStories.last_request.json() == jsonable_encoder(
      [mocks.mock_story()])
  assert spyScrapedUrl.called == True
  assert spyScrapedUrl.last_request.json() == jsonable_encoder([
      project_types.ScrapedUrl(
          published_at=mocks.mock_story().published_at,
          source_name=mocks.mock_story().source.name,
          url=mocks.mock_story().url)
  ])
