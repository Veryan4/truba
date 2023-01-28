from pytest_mock import MockerFixture
from datetime import datetime
from freezegun import freeze_time

from services.story import scraped_url
from shared.types import scraped_url_types


def test_add_scraped_urls(mocker: MockerFixture):

  spy = mocker.patch('services.story.scraped_url.mongo.add_or_update',
                     return_value=True)

  test_list = (scraped_url_types.ScrapedUrl(
      published_at=datetime(2021, 4, 4, 8, 0, 0, 0),
      source_name="BBC",
      url="https://bbc.com/news-story"), )
  assert scraped_url.add_scraped_urls(test_list) == True

  spy.assert_called_once_with(({
      "published_at": datetime(2021, 4, 4, 8, 0, 0, 0),
      "source_name": "BBC",
      "url": "https://bbc.com/news-story"
  }, ), 'ScrapedUrl')


@freeze_time("2021-01-04")
def test_get_by_source_name(mocker: MockerFixture):
  spy = mocker.patch('services.story.scraped_url.mongo.get',
                     return_value=[{
                         "published_at":
                         datetime(2021, 4, 4, 8, 0, 0, 0),
                         "source_name":
                         "BBC",
                         "url":
                         "https://bbc.com/news-story"
                     }])

  assert scraped_url.get_by_source_name("BBC") == (
      "https://bbc.com/news-story", )

  spy.assert_called_once_with(
      'ScrapedUrl', {
          "source_name": "BBC",
          "published_at": {
              '$gte': datetime(2021, 1, 1, 0, 0, 0, 0),
              '$lt': datetime(2021, 1, 4, 0, 0, 0, 0)
          }
      })
