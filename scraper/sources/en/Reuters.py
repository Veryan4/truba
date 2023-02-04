from services.source_scraper import SourceScraper
from services.source_story_parser import SourceStoryParser, log_error
from shared.types import source_types


class Reuters(SourceScraper):

  def __init__(self, source: source_types.Source):
    self.source_story_parser = ReutersParser
    self.rss_feed = self.get_rss_feed(source.rss_feed)
    if self.rss_feed:
      self.stories = self.scrape_stories(source)


class ReutersParser(SourceStoryParser):

  @log_error
  def get_story_author(self):
    return self.article_content.find(
        attrs={'property': 'og:article:author'})['content']

  @log_error
  def get_story_publication_date(self):
    return self.article_content.find(
        'time', attrs={'property': 'og:article:published_time'})['content']

  @log_error
  def get_story_body(self):
    story_body = []
    for body in self.article_content.find_all(
        class_='StandardArticleBody_body'):
      for paragraph_or_element in body.find_all('p', recursive=False):
        story_body.append(paragraph_or_element.get_text())
    story_body = ' '.join(story_body)
    return story_body
