from services.source_scraper import SourceScraper
from services.source_story_parser import SourceStoryParser, log_error
import project_types


class Le_Monde(SourceScraper):

  def __init__(self, source: project_types.Source):
    self.source_story_parser = Le_MondeParser
    self.rss_feed = self.get_rss_feed(source.rss_feed)
    if self.rss_feed:
      self.stories = self.scrape_stories(source)


class Le_MondeParser(SourceStoryParser):


  @log_error
  def get_story_author(self):
    return self.article_content.find(
        attrs={'property': 'og:article:author'})['content']

  @log_error
  def get_story_publication_date(self):
    return self.article_content.find(
        attrs={'property': 'og:article:published_time'})['content']

  @log_error
  def get_story_body(self):
    story_body = []
    for body in self.article_content.find_all(class_="article__content"):
      for paragraph_or_element in body.find_all('p', recursive=False):
        paragraphText = paragraph_or_element.get_text()
        if (paragraphText != 'Article réservé aux abonnés'):
          story_body.append(paragraph_or_element.get_text())
    story_body = " ".join(story_body)
    return story_body
