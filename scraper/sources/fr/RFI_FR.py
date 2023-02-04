from services.source_scraper import SourceScraper
from services.source_story_parser import SourceStoryParser, log_error
from shared.types import source_types


class RFI_FR(SourceScraper):

  def __init__(self, source: source_types.Source):
    self.source_story_parser = RFI_FRParser
    self.rss_feed = self.get_rss_feed(source.rss_feed)
    if self.rss_feed:
      self.stories = self.scrape_stories(source)


class RFI_FRParser(SourceStoryParser):

  @log_error
  def get_story_image_url(self):
    return self.article_content.find(attrs={'itemprop': 'image'})['src']

  @log_error
  def get_story_description(self):
    story_description = None
    try:
      story_description = self.article_content.find(class_="intro").get_text()
    except AttributeError:
      return self.article_content.find(
          attrs={'property': 'og:description'})['content']
    return story_description

  @log_error
  def get_story_author(self):
    return self.article_content.find(
        attrs={'property': 'og:site_name'})['content']

  @log_error
  def get_story_publication_date(self):
    return self.article_content.find(
        attrs={'property': 'article:published_time'})['content']

  @log_error
  def get_story_body(self):
    story_body = []
    for body in self.article_content.find_all(
        attrs={'itemprop': 'articleBody'}):
      for paragraph_or_element in body.find_all('p', recursive=False):
        paragraph_count = 0
        for paragraph in paragraph_or_element.find_all('p', recursive=True):
          story_body.append(paragraph.get_text())
          paragraph_count = paragraph_count + 1
        if (paragraph_count == 0):
          story_body.append(paragraph_or_element.get_text())
    story_body = " ".join(story_body)
    return story_body
