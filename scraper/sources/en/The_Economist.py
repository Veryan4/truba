from services.source_scraper import SourceScraper
from services.source_story_parser import SourceStoryParser, log_error
import project_types


class The_Economist(SourceScraper):

  def __init__(self, source: project_types.Source):
    self.source_story_parser = The_EconomistParser
    self.rss_feed = self.get_rss_feed(source.rss_feed)
    if self.rss_feed:
      self.stories = self.scrape_stories(source)


class The_EconomistParser(SourceStoryParser):

  @log_error
  def get_story_author(self):
    return self.article_content.find(attrs={'itemprop': 'author'})['content']

  @log_error
  def get_story_publication_date(self):
    return self.article_content.find(
        attrs={'itemprop': 'datePublished'})['content']

  @log_error
  def get_story_body(self):
    story_body = None
    for body in self.article_content.find_all(attrs={'itemprop': 'text'}):
      for paragraph_or_element in body.find_all('p', recursive=False):
        story_body.append(paragraph_or_element.get_text())
    story_body = " ".join(story_body)
    return story_body
