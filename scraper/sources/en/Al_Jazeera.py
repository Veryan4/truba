from services.source_scraper import SourceScraper
from services.source_story_parser import SourceStoryParser, log_error
from shared.types import source_types


class Al_Jazeera(SourceScraper):

  def __init__(self, source: source_types.Source):
    self.source_story_parser = Al_JazeeraParser
    self.rss_feed = self.get_rss_feed(source.rss_feed)
    if self.rss_feed:
      self.stories = self.scrape_stories(source)


class Al_JazeeraParser(SourceStoryParser):

  @log_error
  def get_story_publication_date(self):
    return self.article_content.find(class_="date-simple").get_text()

  @log_error
  def get_story_body(self):
    story_body = []
    for body in self.article_content.find(class_="wysiwyg"):
      for paragraph_or_element in body.find_all('p', recursive=False):
        story_body.append(paragraph_or_element.get_text())
    story_body = " ".join(story_body)
    return story_body
