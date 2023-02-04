from services.source_scraper import SourceScraper
from services.source_story_parser import SourceStoryParser, log_error
from shared.types import source_types


class France24_FR(SourceScraper):

  def __init__(self, source: source_types.Source):
    self.source_story_parser = France24_FRParser
    self.rss_feed = self.get_rss_feed(source.rss_feed)
    if self.rss_feed:
      self.stories = self.scrape_stories(source)


class France24_FRParser(SourceStoryParser):

  @log_error
  def get_story_title(self):
    return self.article_content.find('title').get_text()

  @log_error
  def get_story_author(self):
    return None

  @log_error
  def get_story_publication_date(self):
    return self.article_content.find('time', attrs={'pubdate':
                                                    'pubdate'})['datetime']

  @log_error
  def get_story_body(self):
    story_body = []
    story_description = self.article_content.find(
        attrs={'property': 'og:description'})['content']
    story_body.append(story_description)
    for body in self.article_content.find_all(class_="t-content__body"):
      for paragraph_or_element in body.find_all('p'):
        story_body.append(paragraph_or_element.get_text())
    story_body = " ".join(story_body)
    return story_body
