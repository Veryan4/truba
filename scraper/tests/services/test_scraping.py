from pytest_mock import MockerFixture
import pytest
from datetime import datetime
from freezegun import freeze_time
from fastapi.encoders import jsonable_encoder

from services import scraper
from shared.types import story_types, scraped_url_types


@pytest.fixture(autouse=True)  #before each
def run_around_tests(mocker: MockerFixture):
  mocker.patch('services.scraper.tracing.log')
  mocker.patch('shared.setup.get_base_core_service_url',
               return_value="http://127.0.0.1:5057")
  yield


def test_get_sources(requests_mock, mocker: MockerFixture):
  mocker.patch('os.getenv', return_value="en")
  requests_mock.get("http://127.0.0.1:5057/sources/en",
                    json=jsonable_encoder([story_types.mock_story().source]))

  assert scraper.get_sources() == (story_types.mock_story().source, )


def test_get_scraped_urls(requests_mock, mocker: MockerFixture):
  requests_mock.get(
      "http://127.0.0.1:5057/scraped?source_name=New%20York%20Times",
      json=jsonable_encoder(["http://news.artcile"]))

  assert scraper.get_scraped_urls("New York Times") == ["http://news.artcile"]


def test_push_stories_to_core(requests_mock, mocker: MockerFixture):
  spyStories = requests_mock.post("http://127.0.0.1:5057/stories")
  spyScrapedUrl = requests_mock.post("http://127.0.0.1:5057/scraped")

  scraper.push_stories_to_core(story_types.mock_story().source,
                               [story_types.mock_story()])

  assert spyStories.called == True
  assert spyStories.last_request.json() == jsonable_encoder(
      [story_types.mock_story()])
  assert spyScrapedUrl.called == True
  assert spyScrapedUrl.last_request.json() == jsonable_encoder([
      scraped_url_types.ScrapedUrl(
          published_at=story_types.mock_story().published_at,
          source_name=story_types.mock_story().source.name,
          url=story_types.mock_story().url)
  ])
