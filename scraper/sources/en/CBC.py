from services.source_scraper import SourceScraper
from services.source_story_parser import SourceStoryParser, log_error
from shared.types import source_types


class CBC(SourceScraper):

  def __init__(self, source: source_types.Source):
    self.source_story_parser = CBCParser
    self.rss_feed = self.get_rss_feed(source.rss_feed)
    if self.rss_feed:
      self.stories = self.scrape_stories(source)


class CBCParser(SourceStoryParser):

  @log_error
  def get_story_author(self):
    story_author = []
    for author_element in self.article_content.find_all(class_="authorText"):
      for span_or_element in author_element.find_all('a', recursive=False):
        story_author.append(span_or_element.get_text())
    story_author = " ".join(story_author)
    return story_author

  @log_error
  def get_story_publication_date(self):
    return self.article_content.find('time', class_="timeStamp")['datetime']

  @log_error
  def get_story_body(self):
    story_body = []
    for body in self.article_content.find_all(class_="story"):
      for paragraph_or_element in body.find_all('p', recursive=False):
        story_body.append(paragraph_or_element.get_text())
    story_body = " ".join(story_body)
    return story_body
