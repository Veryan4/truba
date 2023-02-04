from services.source_scraper import SourceScraper
from services.source_story_parser import SourceStoryParser, log_error
from shared.types import source_types


class The_Atlantic(SourceScraper):

  def __init__(self, source: source_types.Source):
    self.source_story_parser = The_AtlanticParser
    self.rss_feed = self.get_rss_feed(source.rss_feed)
    if self.rss_feed:
      self.stories = self.scrape_stories(source)

  def get_rss_items(self):
    return self.rss_feed.find_all(attrs={'class': 'article'})

  @log_error
  def get_rss_item_pubdate(self, item):
    return item.find(attrs={'class': 'date'}).text

  @log_error
  def get_rss_item_title(self, item):
    return item.find('h2').find('a').text

  def get_rss_item_description(self, item):
    return None

  @log_error
  def get_rss_item_url(self, item):
    return item.find('h2').find('a')['href']

class The_AtlanticParser(SourceStoryParser):

  @log_error
  def get_story_publication_date(self):
    return self.article_content.find(
        attrs={'property': 'article:published_time'})['content']

  @log_error
  def get_story_body(self):
    story_body = []
    for body in self.article_content.find_all(
        attrs={'itemprop': 'articleBody'}):
      for paragraph_or_element in body.find_all('p', recursive=False):
        story_body.append(paragraph_or_element.get_text())
    story_body = " ".join(story_body)
    return story_body
