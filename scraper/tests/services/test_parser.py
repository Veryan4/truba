from pytest_mock import MockerFixture
import pytest
from datetime import datetime
from freezegun import freeze_time
from fastapi.encoders import jsonable_encoder

from services import parser
from shared.types import story_types


@pytest.fixture(autouse=True)  #before each
def run_around_tests(mocker: MockerFixture):
  mocker.patch('services.parser.spacy.load')
  mocker.patch('shared.tracing.log')
  mocker.patch('services.parser.setup.get_base_core_service_url',
               return_value="http://127.0.0.1:5057")
  yield


def test_get_author_by_name(requests_mock, mocker: MockerFixture):
  requests_mock.get(
      "http://127.0.0.1:5057/authors/name?author_name=Tom%20Lundy",
      json=jsonable_encoder(story_types.mock_story().author))

  assert parser.get_author_by_name(
      'Tom Lundy') == story_types.mock_story().author
