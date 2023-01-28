#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
import re
import requests
import os
import traceback
from typing import List, Tuple, Optional
from fastapi.encoders import jsonable_encoder
from urllib.parse import quote
from bs4 import BeautifulSoup

from services import parser
from shared.types import story_types, source_types, scraped_url_types
from shared import setup, tracing

current_module = 'Scraping'


def reset_sources() -> None:
  """Resets the list of sources to make sure any changes are picked up

    """

  response = requests.get(setup.get_base_core_service_url() + '/sources/reset')
  if response.status_code == 404:
    tracing.log(current_module, 'error', 'Unable to reset sources')


def get_sources() -> Optional[Tuple[source_types.Source]]:
  """Retrieves the list of current sources from the Core service.

    Returns:
        A List of Sources if found, None if not found.

    """

  response = requests.get(setup.get_base_core_service_url() + '/sources/' +
                          os.getenv("SCRAPER_LANGUAGE"))
  if response.status_code == 404:
    tracing.log(current_module, 'error', 'No Sources found')
    return None
  source_dict = response.json()
  return tuple(source_types.Source(**source) for source in source_dict)


def get_scraped_urls(source_name: str) -> List[str]:
  """Retrieves the list of urls of stories which have been previously
  scraped for a given source.

    Args:
        source_name: The name of the source.

    Returns:
        The list of the source's previously scrapped urls.

    """

  response = requests.get(setup.get_base_core_service_url() +
                          '/scraped?source_name=' + quote(source_name))
  if response.status_code == 404:
    tracing.log(current_module, 'error',
                'failed to get ScrapedUrls for ' + source_name)
    return []
  return response.json()


def get_rss_feed_items(rss_url: str):
  """Retrieves a list of RSS feed items which are parsed by BeautifulSoup.

    Args:
        rss_url: The url of the RSS feed.

    Returns:
        A list of RSS feed items.

    """

  response = requests.get(rss_url, headers={'User-Agent': 'My User Agent 1.0'})
  if not response:
    tracing.log(current_module, 'error', 'Failed to get RSS feed')
    return []
  rss_feed = BeautifulSoup(response.content, features='xml') if (
      'xml' in rss_url) else BeautifulSoup(response.content,
                                           features="html.parser")
  return rss_feed.findAll('item')


def push_stories_to_core(source: source_types.Source,
                         stories: List[story_types.Story]):
  """Submits the scraped stories for a given source back to the Core
  service for storage.

    Args:
        source: The source the the new stories.
        stories: The list of stories to store.

    """

  json_to_push = jsonable_encoder(stories)
  requests.post(setup.get_base_core_service_url() + "/stories",
                json=json_to_push)
  recently_scraped_urls = [
      scraped_url_types.ScrapedUrl(published_at=scraped_story.published_at,
                                   source_name=source.name,
                                   url=scraped_story.url)
      for scraped_story in stories
  ]
  if recently_scraped_urls:
    scrapped_json = jsonable_encoder(recently_scraped_urls)
    requests.post(setup.get_base_core_service_url() + "/scraped",
                  json=scrapped_json)
  message_to_log = str(
      len(stories)) + " stories were extracted from the Source: " + source.name
  tracing.log(current_module, 'info', message_to_log)


def scrape():
  """Performs the entire Scraping operation from start to finish.

    """

  reset_sources()
  sources = get_sources()
  if not sources:
    return
  current_date = datetime.now()
  for source in sources:
    stories = []
    scraped_urls = get_scraped_urls(source.name)
    articles_items = get_rss_feed_items(source.rss_feed)
    for article_item in articles_items:
      article_url = None
      if article_item.find('link'):
        article_url = article_item.find('link').text
      if not article_url:
        for element_attribute in article_item:
          url_pattern = re.compile(r'http(\S*)')
          matching = url_pattern.match(str(element_attribute))
          if matching:
            article_url = str(matching.group())
            break
      if not article_url or article_url in scraped_urls:
        continue
      story = parser.get_story(source, article_url, article_item)
      if story:
        scraped_urls.append(story.url)
        time_since_published = current_date.replace(
            tzinfo=None) - story.published_at.replace(tzinfo=None)
        if time_since_published.days < 4:
          stories.append(story)
    try:
      push_stories_to_core(source, stories)
      # solr is temporarily removed
      #refill_solr()
    except Exception:
      message_to_log = traceback.format_exc()
      tracing.log(current_module, 'error', message_to_log)


def refill_solr():
  """Attempts to trigger the Solr re-indexing after new stories have been added.

    """

  result = requests.get(setup.get_base_core_service_url() + "/solr/reset")
  tracing.log(current_module, 'info', result)
