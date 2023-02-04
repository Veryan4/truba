from services.source_scraper import SourceScraper
from services.source_story_parser import SourceStoryParser, log_error
from shared.types import source_types


class Der_Spiegel(SourceScraper):

  def __init__(self, source: source_types.Source):
    self.source_story_parser = Der_SpiegelParser
    self.rss_feed = self.get_rss_feed(source.rss_feed)
    if self.rss_feed:
      self.stories = self.scrape_stories(source)


class Der_SpiegelParser(SourceStoryParser):

  @log_error
  def get_story_publication_date(self):
    return self.article_content.find(attrs={'name': 'date'})['content']

  @log_error
  def get_story_body(self):
    story_body = []
    for body in self.article_content.find_all(
        attrs={'data-article-el': 'body'}):
      for paragraph_or_element in body.find_all('p', recursive=False):
        story_body.append(paragraph_or_element.get_text())
    story_body = ' '.join(story_body)
    return story_body
