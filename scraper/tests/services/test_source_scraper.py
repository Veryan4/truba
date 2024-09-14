from pytest_mock import MockerFixture
import pytest
from datetime import datetime
from freezegun import freeze_time
from fastapi.encoders import jsonable_encoder

from services import source_scraper
import project_types
from tests import mocks


@pytest.fixture(autouse=True)  #before each
def run_around_tests(mocker: MockerFixture):
  mocker.patch('services.source_scraper.tracing.log')
  mocker.patch('shared.setup.get_base_core_service_url',
               return_value="http://127.0.0.1:5057")
  yield

#def test_get_scraped_urls(requests_mock, mocker: MockerFixture):
#  requests_mock.get(
#      "http://127.0.0.1:5057/scraped?source_name=New%20York%20Times",
#      json=jsonable_encoder(["http://news.artcile"]))
#  dummy_source = source_scraper.SourceScraper(mocks.mock_source())
#  assert dummy_source.get_scraped_urls("New York Times") == ["http://news.artcile"]