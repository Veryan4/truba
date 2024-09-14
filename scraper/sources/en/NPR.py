from services.source_scraper import SourceScraper
from services.source_story_parser import SourceStoryParser, log_error
import project_types


class NPR(SourceScraper):

  def __init__(self, source: project_types.Source):
    self.source_story_parser = NPRParser
    self.rss_feed = self.get_rss_feed(source.rss_feed)
    if self.rss_feed:
      self.stories = self.scrape_stories(source)


class NPRParser(SourceStoryParser):

  @log_error
  def get_story_image_url(self):
    return self.article_content.find(attrs={
        'id': 'storytext'
    }).find('img')['src']

  @log_error
  def get_story_title(self):
    return self.article_content.find(class_="storytitle").find('h1').text

  @log_error
  def get_story_description(self):
    return None

  @log_error
  def get_story_author(self):
    return self.article_content.find(attrs={'rel': 'author'}).text

  @log_error
  def get_story_publication_date(self):
    return self.article_content.find('time')['datetime']

  @log_error
  def get_story_body(self):
    story_body = []
    for body in self.article_content.find_all(attrs={'id': 'storytext'}):
      for paragraph_or_element in body.find_all('p', recursive=False):
        story_body.append(paragraph_or_element.get_text())
    story_body = " ".join(story_body)
    return story_body
