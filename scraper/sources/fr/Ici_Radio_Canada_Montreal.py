from services.source_scraper import SourceScraper
from services.source_story_parser import SourceStoryParser, log_error
from shared.types import source_types


class Ici_Radio_Canada_Montreal(SourceScraper):

  def __init__(self, source: source_types.Source):
    self.source_story_parser = Ici_Radio_Canada_MontrealParser
    self.rss_feed = self.get_rss_feed(source.rss_feed)
    if self.rss_feed:
      self.stories = self.scrape_stories(source)


class Ici_Radio_Canada_MontrealParser(SourceStoryParser):

  @log_error
  def get_story_author(self):
    return self.article_content.find(attrs={'name': 'rc.domaine'})['content']

  @log_error
  def get_story_publication_date(self):
    return self.article_content.find(
        attrs={'name': 'dc.date.created'})['content']

  @log_error
  def get_story_body(self):
    story_body = []
    tags = ['blockquote', 'p', 'h2']
    for body in self.article_content.find_all(class_='lead-container'):
      for paragraph_or_element in body.find_all(tags, recursive=False):
        story_body.append(paragraph_or_element.get_text())
    for body_element in self.article_content.find_all(class_='redactionals'):
      for paragraph in body_element.find_all(tags, recursive=False):
        story_body.append(paragraph.get_text())
    story_body = ' '.join(story_body)
    return story_body
