from services.source_scraper import SourceScraper
from services.source_story_parser import SourceStoryParser, log_error
from shared.types import source_types


class Le_Devoir_Montreal(SourceScraper):

  def __init__(self, source: source_types.Source):
    self.source_story_parser = Le_Devoir_MontrealParser
    self.rss_feed = self.get_rss_feed(source.rss_feed)
    if self.rss_feed:
      self.stories = self.scrape_stories(source)


class Le_Devoir_MontrealParser(SourceStoryParser):

  @log_error
  def get_story_author(self):
    story_author = None
    for element in self.article_content.find_all(class_='author'):
      for author_info in element.find_all('span', recursive=False):
        story_author = author_info.get_text()
    return story_author

  @log_error
  def get_story_publication_date(self):
    story_publication_date = None
    for time_element in self.article_content.find_all(class_='author'):
      for time_info in time_element.find_all('time', recursive=True):
        story_publication_date = time_info.get_text()
    return story_publication_date

  @log_error
  def get_story_body(self):
    story_body = []
    for body in self.article_content.find_all(class_='editor'):
      for paragraph_or_element in body.find_all('p', recursive=False):
        story_body.append(paragraph_or_element.get_text())
    story_body = " ".join(story_body)
    return story_body
