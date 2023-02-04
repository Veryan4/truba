from services.source_scraper import SourceScraper
from services.source_story_parser import SourceStoryParser, log_error
from shared.types import source_types


class Phys_Org(SourceScraper):

  def __init__(self, source: source_types.Source):
    self.source_story_parser = Phys_OrgParser
    self.rss_feed = self.get_rss_feed(source.rss_feed)
    if self.rss_feed:
      self.stories = self.scrape_stories(source)


class Phys_OrgParser(SourceStoryParser):

  @log_error
  def get_story_author(self):
    return self.article_content.find(class_="article-byline").get_text()

  @log_error
  def get_story_publication_date(self):
    return None

  @log_error
  def get_story_body(self):
    story_body = []
    for body in self.article_content.find_all(
        attrs={'property': 'articleBody'}):
      for paragraph_or_element in body.find_all('p', recursive=False):
        story_body.append(paragraph_or_element.get_text())
    story_body = " ".join(story_body)
    return story_body
