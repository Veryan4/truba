import requests
import os
import traceback
import importlib
import logging
from typing import List, Tuple, Optional
from fastapi.encoders import jsonable_encoder

import project_types

logger = logging.getLogger(__name__)


def reset_sources() -> None:
  """Resets the list of sources to make sure any changes are picked up

    """

  response = requests.get(os.getenv("CORE_URL") + '/sources/reset')
  if response.status_code == 404:
    logger.error('Unable to reset sources')


def get_sources() -> Optional[Tuple[project_types.Source]]:
  """Retrieves the list of current sources from the Core service.

    Returns:
        A List of Sources if found, None if not found.

    """

  response = requests.get(os.getenv("CORE_URL") + '/sources/' +
                          os.getenv("SCRAPER_LANGUAGE"))
  if response.status_code == 404:
    logger.error('No Sources found')
    return None
  source_dict = response.json()
  return tuple(project_types.Source(**source) for source in source_dict)


def push_stories_to_core(source: project_types.Source,
                         stories: List[project_types.Story]):
  """Submits the scraped stories for a given source back to the Core
  service for storage.

    Args:
        source: The source the the new stories.
        stories: The list of stories to store.

    """

  if not stories:
    logger.info('no stories to push for ' + source.name)
    return
  json_to_push = jsonable_encoder(stories)
  requests.post(os.getenv("CORE_URL") + '/stories',
                json=json_to_push)
  recently_scraped_urls = [
      project_types.ScrapedUrl(published_at=scraped_story.published_at,
                                   source_name=source.name,
                                   url=scraped_story.url)
      for scraped_story in stories
  ]
  if recently_scraped_urls:
    scrapped_json = jsonable_encoder(recently_scraped_urls)
    requests.post(os.getenv("CORE_URL") + '/scraped',
                  json=scrapped_json)
  message_to_log = str(
      len(stories)) + ' stories were extracted from the Source: ' + source.name
  logger.info(message_to_log)


def get_source_class(source: project_types.Source):
  """Loads the appropriate Source module for extracting the information.

    Args:
        source: The news source.

    Returns:
        The class of the loaded module.

    """

  source_dir = 'sources.' + source.language + '.'
  class_name = source.name.replace(' ', '_')
  module = importlib.import_module(source_dir + str(class_name))
  return getattr(module, class_name)


def scrape():
  """Performs the entire Scraping operation from start to finish.

    """

  reset_sources()
  sources = get_sources()
  if not sources:
    return
  for source in sources:
    try:
      soucer_scraper = get_source_class(source)
      source_scraped = soucer_scraper(source)
      stories = source_scraped.stories
      push_stories_to_core(source, stories)
    except Exception:
      message_to_log = traceback.format_exc()
      logger.error(message_to_log)
