from services.source_scraper import SourceScraper
from services.source_story_parser import SourceStoryParser, log_error
import project_types


class Channel_News_Asia(SourceScraper):

  def __init__(self, source: project_types.Source):
    self.source_story_parser = Channel_News_AsiaParser
    self.rss_feed = self.get_rss_feed(source.rss_feed)
    if self.rss_feed:
      self.stories = self.scrape_stories(source)

  def get_rss_items(self):
    return self.rss_feed.find_all(id='item')

  def get_rss_item_pubdate(self, item):
    return None

  @log_error
  def get_rss_item_title(self, item):
    return item.find('a').text

  @log_error
  def get_rss_item_description(self, item):
    return item.find('div').text

  @log_error
  def get_rss_item_url(self, item):
    return item.find('a')['href']

class Channel_News_AsiaParser(SourceStoryParser):

  @log_error
  def get_story_publication_date(self):
    return self.article_content.find(class_="article-publish").get_text()

  @log_error
  def get_story_body(self):
    story_body = []
    for body in self.article_content.find(class_="text-long"):
      for paragraph_or_element in body.find_all('p', recursive=False):
        story_body.append(paragraph_or_element.get_text())
    story_body = " ".join(story_body)
    return story_body
