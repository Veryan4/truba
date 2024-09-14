from pytest_mock import MockerFixture
import pytest
from datetime import datetime
from freezegun import freeze_time
from fastapi.encoders import jsonable_encoder

from services import formatter
from tests import mocks


@pytest.fixture(autouse=True)  #before each
def run_around_tests(mocker: MockerFixture):
  mocker.patch('services.formatter.spacy.load')
  mocker.patch('shared.tracing.log')
  mocker.patch('services.formatter.setup.get_base_core_service_url',
               return_value="http://127.0.0.1:5057")
  yield


def test_get_author_by_name(requests_mock, mocker: MockerFixture):
  requests_mock.get(
      "http://127.0.0.1:5057/authors/name?author_name=Tom%20Lundy",
      json=jsonable_encoder(mocks.mock_story().author))

  assert formatter.get_author_by_name(
      'Tom Lundy') == mocks.mock_story().author
