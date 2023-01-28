# -*- coding: utf-8 -*-
import traceback

import sys

sys.path.append('../')

from shared import tracing

current_module = 'source_parsers'


# This class is for the format of an article after being parsed
class NPR:

  def __init__(self, article_content):

    self.article_content = article_content

  def get_story_image_url(self):
    story_image_url = None
    try:
      story_image_url = self.article_content.find(attrs={
          'id': 'storytext'
      }).find('img')['src']
    except Exception:
      message_to_log = traceback.format_exc()
      tracing.log(current_module, 'exception', message_to_log)
    return story_image_url

  def get_story_title(self):
    story_title = None
    try:
      story_title = self.article_content.find(
          class_="storytitle").find('h1').text
    except Exception:
      message_to_log = traceback.format_exc()
      tracing.log(current_module, 'exception', message_to_log)
    return story_title

  def get_story_description(self):
    return None

  def get_story_author(self):
    story_author = None
    try:
      story_author = self.article_content.find(attrs={'rel': 'author'}).text
    except Exception:
      message_to_log = traceback.format_exc()
      tracing.log(current_module, 'exception', message_to_log)
    return story_author

  def get_story_publication_date(self):
    story_publication_date = None
    try:
      story_publication_date = self.article_content.find('time')['datetime']
    except Exception:
      message_to_log = traceback.format_exc()
      tracing.log(current_module, 'exception', message_to_log)
    return story_publication_date

  def get_story_body(self):
    story_body = None
    try:
      story_body = []
      for body in self.article_content.find_all(attrs={'id': 'storytext'}):
        for paragraph_or_element in body.find_all('p', recursive=False):
          story_body.append(paragraph_or_element.get_text())
      story_body = " ".join(story_body)
    except Exception:
      message_to_log = traceback.format_exc()
      tracing.log(current_module, 'exception', message_to_log)
    return story_body
