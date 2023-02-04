from services.source_scraper import SourceScraper
from services.source_story_parser import SourceStoryParser, log_error
from shared.types import source_types


class South_China_Morning_Post(SourceScraper):

  def __init__(self, source: source_types.Source):
    self.source_story_parser = South_China_Morning_PostParser
    self.rss_feed = self.get_rss_feed(source.rss_feed)
    if self.rss_feed:
      self.stories = self.scrape_stories(source)


class South_China_Morning_PostParser(SourceStoryParser):

  @log_error
  def get_story_description(self):
    return self.article_content.find(attrs={'name': 'description'})['content']

  @log_error
  def get_story_author(self):
    return self.article_content.find(attrs={'name': 'cse_author'})['content']

  @log_error
  def get_story_publication_date(self):
    return self.article_content.find(
        attrs={'property': 'og:updated_time'})['content']

  @log_error
  def get_story_body(self):
    story_body = []
    for body in self.article_content.find(class_="details__body"):
      for paragraph_or_element in body.find_all(class_="generic-article__body",
                                                recursive=False):
        story_body.append(paragraph_or_element.get_text())
    story_body = " ".join(story_body)
    return story_body
