from services.source_scraper import SourceScraper
from services.source_story_parser import SourceStoryParser, log_error
from shared.types import source_types


class NBC(SourceScraper):

  def __init__(self, source: source_types.Source):
    self.source_story_parser = NBCParser
    self.rss_feed = self.get_rss_feed(source.rss_feed)
    if self.rss_feed:
      self.stories = self.scrape_stories(source)


class NBCParser(SourceStoryParser):

  @log_error
  def get_story_author(self):
    return self.article_content.find(attrs={'data-test': 'byline'}).text

  @log_error
  def get_story_publication_date(self):
    return self.article_content.find(
        attrs={'itemprop': 'datePublished'})['content']

  @log_error
  def get_story_body(self):
    story_body = []
    for body in self.article_content.find_all(class_="article-body__content"):
      for paragraph_or_element in body.find_all('p', recursive=False):
        story_body.append(paragraph_or_element.get_text())
    story_body = " ".join(story_body)
    return story_body
