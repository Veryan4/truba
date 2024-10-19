import traceback
from bs4 import BeautifulSoup
import logging


logger = logging.getLogger(__name__)


def log_error(func):

  def inner(*args):
    try:
      return func(*args)
    except Exception:
      message_to_log = traceback.format_exc()
      logger.error(message_to_log)
      return None

  return inner


class SourceStoryParser:

  def __init__(self, article_content: BeautifulSoup):
    self.article_content = article_content
    self.story_image_url = self.get_story_image_url()
    self.story_title = self.get_story_title()
    self.story_description = self.get_story_description()
    self.story_author = self.get_story_author()
    self.story_publication_date = self.get_story_publication_date()
    self.story_body = self.get_story_body()

  @log_error
  def get_story_image_url(self):
    return self.article_content.find(attrs={'property': 'og:image'})['content']

  @log_error
  def get_story_title(self):
    return self.article_content.find(attrs={'property': 'og:title'})['content']

  @log_error
  def get_story_description(self):
    return self.article_content.find(
        attrs={'property': 'og:description'})['content']

  @log_error
  def get_story_author(self):
    return self.article_content.find(attrs={'name': 'author'})['content']

  @log_error
  def get_story_publication_date(self):
    return self.article_content.find(class_='date-simple').get_text()

  @log_error
  def get_story_body(self):
    story_body = []
    for body in self.article_content.find(class_='wysiwyg'):
      for paragraph_or_element in body.find_all('p', recursive=False):
        story_body.append(paragraph_or_element.get_text())
    story_body = ' '.join(story_body)
    return story_body
