from bs4 import BeautifulSoup
from datetime import datetime
import re
import requests
from typing import List
from urllib.parse import quote

from services import formatter
from services.source_story_parser import SourceStoryParser, log_error
from services import rss_item
import project_types
from shared import setup, tracing

current_module = 'Source Scraper'


class SourceScraper:

  def __init__(self, source: project_types.Source):
    self.source_story_parser = SourceStoryParser
    self.rss_feed = self.get_rss_feed(source.rss_feed)
    if self.rss_feed:
      self.stories = self.scrape_stories(source)

  def scrape_stories(self, source: project_types.Source):
    scraped_urls = self.get_scraped_urls(source.name)
    rss_items = self.extract_rss_items()
    return self.scrape_source(source, rss_items, scraped_urls)

  def get_rss_feed(self, rss_url: str) -> BeautifulSoup:
    response = requests.get(rss_url,
                            headers={'User-Agent': 'My User Agent 1.0'})
    if not response:
      tracing.log(current_module, 'error', 'Failed to get RSS feed')
      return None
    try:
      return BeautifulSoup(response.content, features='xml')
    except Exception:
      return BeautifulSoup(response.content, features='html.parser')

  def extract_rss_items(self) -> List[rss_item.RssItem]:
    items = self.get_rss_items()
    return [
        rss_item.RssItem(pubdate=self.get_rss_item_pubdate(item),
                         title=self.get_rss_item_title(item),
                         description=self.get_rss_item_description(item),
                         url=self.get_rss_item_url(item)) for item in items
    ]

  def get_rss_items(self) -> List[BeautifulSoup]:
    return self.rss_feed.find_all('item')

  @log_error
  def get_rss_item_pubdate(self, item: BeautifulSoup) -> str:
    return item.find('pubDate').text

  @log_error
  def get_rss_item_title(self, item: BeautifulSoup) -> str:
    return item.find('title').text

  @log_error
  def get_rss_item_description(self, item: BeautifulSoup) -> str:
    return item.find('description').text

  @log_error
  def get_rss_item_url(self, item: BeautifulSoup) -> str:
    return item.find('link').text

  def get_scraped_urls(self, source_name: str) -> List[str]:
    response = requests.get(setup.get_base_core_service_url() +
                            '/scraped?source_name=' + quote(source_name))
    if response.status_code == 404:
      tracing.log(current_module, 'error',
                  'failed to get ScrapedUrls for ' + source_name)
      return []
    return response.json()

  def get_article_content(self, url: str) -> BeautifulSoup:
    page = requests.get(url, headers={'User-Agent': 'My User Agent 1.0'})
    return BeautifulSoup(page.content, 'html.parser')

  def scrape_source(self, source: project_types.Source,
                     rss_items: List[rss_item.RssItem],
                     scraped_urls: List[str]) -> List[project_types.Story]:
    stories = []
    current_date = datetime.now()
    for article_item in rss_items:
      article_url = None
      if article_item.url:
        article_url = article_item.url
      if not article_url:
        for element_attribute in article_item:
          url_pattern = re.compile(r'http(\S*)')
          matching = url_pattern.match(str(element_attribute))
          if matching:
            article_url = str(matching.group())
            break
      if not article_url or article_url in scraped_urls:
        continue
      article_content = self.get_article_content(article_url)
      parsed_story = self.source_story_parser(article_content)
      story = formatter.format_story(source, article_url, parsed_story,
                                     article_item)
      if story:
        scraped_urls.append(story.url)
        time_since_published = current_date.replace(
            tzinfo=None) - story.published_at.replace(tzinfo=None)
        if time_since_published.days < 4:
          stories.append(story)
    return stories
