from services.source_scraper import SourceScraper
from services.source_story_parser import SourceStoryParser, log_error
import project_types


class Lapresse(SourceScraper):

  def __init__(self, source: project_types.Source):
    self.source_story_parser = LapresseParser
    self.rss_feed = self.get_rss_feed(source.rss_feed)
    if self.rss_feed:
      self.stories = self.scrape_stories(source)


class LapresseParser(SourceStoryParser):

  @log_error
  def get_story_description(self):
    story_description = None
    try:
      for paragraph_or_element in self.article_content.find_all(
          'p', class_="lead", recursive=True):
        story_description = paragraph_or_element.get_text()
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
    tags = ['p', 'h2', 'h3']
    for body in self.article_content.find_all(class_="articleBody"):
      for paragraph_or_element in body.find_all(tags,
                                                class_="paragraph",
                                                recursive=False):
        paragraphText = paragraph_or_element.get_text()
        if (paragraphText != 'Agence France-Presse'):
          story_body.append(paragraphText)
    story_body = " ".join(story_body)
    return story_body
