#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import traceback
import importlib
import os
from typing import Optional, Tuple, List
from urllib.parse import quote
from datetime import datetime
from collections import Counter
from dateutil import parser
import spacy

from shared import setup, tracing
from shared.types import story_types, source_types, entity_types, author_types, keyword_types

current_module = 'Parser'

# SpaCy can only load one language at a time
# That is why there is an image per language
nlp = None
if str(os.getenv("SCRAPER_LANGUAGE")) == 'fr':
  nlp = spacy.load("fr_core_news_sm")
else:
  nlp = spacy.load("en_core_web_sm")


def get_article_content(url: str):
  """Retrives the BeautifulSoup html for a given website.

    Args:
        url: the internet address of the website.

    Returns:
        BeautifulSoup type object which contains the HTML.

    """

  page = requests.get(url, headers={'User-Agent': 'My User Agent 1.0'})
  return BeautifulSoup(page.content, 'html.parser')


def get_author_by_name(author_name: str) -> Optional[author_types.Author]:
  """Searches the Core service to find the author if they have been
  previously saved.

    Args:
        author_name: The name of the author.

    Returns:
        An Author if found, None if not found.

    """

  author = None
  response = requests.get(setup.get_base_core_service_url() +
                          '/authors/name?author_name=' + quote(author_name))
  if response.status_code == 404:
    return None
  author_dict = response.json()
  author = author_types.Author(**author_dict)
  return author


def get_entities_and_keywords(
    text: str
) -> Tuple[List[entity_types.EntityInStory],
           List[keyword_types.KeywordInStory]]:
  """Extacts the Entities and the Keywords of any given text.

    Args:
        text: Either the Title, Body, or Summary of the article.

    Returns:
        The unique Entities and Keywords of the text.

    """

  entities = []
  lower_case_entity_texts = []
  keywords = []
  ignore_labels = ('CARDINAL', 'DATE', 'ORDINAL', 'TIME', 'EVENT', 'QUANTITY')
  doc = nlp(text)
  if doc.ents:
    words = tuple(token.text.lower() for token in doc
                  if token.text and not token.is_stop and not token.is_punct)
    word_freq = Counter(words)
    for ent in doc.ents:
      if not ent.text:
        continue
      text = ent.text.lower()
      if text not in lower_case_entity_texts:
        if ent.label_ and ent.label_ not in ignore_labels:
          lower_case_entity_texts.append(text)
          links = text + ent.label_
          entity = entity_types.Entity(text=ent.text,
                                       type=ent.label_,
                                       links=links)
          entity_in_story = entity_types.EntityInStory(
              entity=entity, frequency=word_freq[text])
          entities.append(entity_in_story)
  lemmas = tuple(token.lemma_.lower() for token in doc
                 if token.lemma_ and token.is_alpha and token.pos_ == 'NOUN'
                 and not token.is_stop and not token.is_punct)
  lemma_freq = Counter(lemmas)
  unique_lemmas = set(lemmas)
  for lemma in unique_lemmas:
    keyword = keyword_types.Keyword(text=lemma,
                                    language=os.getenv('SCRAPER_LANGUAGE'))
    keyword_in_story = keyword_types.KeywordInStory(
        keyword=keyword, frequency=lemma_freq[lemma])
    keywords.append(keyword_in_story)
  return entities, keywords


def get_source_class(source: source_types.Source, article_url: str):
  """Loads the appropriate Source module for extracting the information.

    Args:
        source: The news source.
        article_url: The page the news is hosted on.

    Returns:
        The class of the loaded module.

    """

  source_dir = "sources." + source.language + "."
  class_name = source.name.replace(' ', '_')
  module = importlib.import_module(source_dir + str(class_name))
  source_class = getattr(module, class_name)
  article_content = get_article_content(article_url)
  return source_class(article_content)


def get_story(source: source_types.Source, article_url: str,
              rss_item) -> Optional[story_types.Story]:
  """Extracts and parses the news story of a given url.

    Args:
        source: The news source.
        article_url: The page the news is hosted on.
        rss_item: The BeautifulSoup object of the RSS feed the
          story was located in.

    Returns:
        The news Story if successful, None if not.

    """

  try:
    source_class = get_source_class(source, article_url)

    image_url = source_class.get_story_image_url()
    title = source_class.get_story_title()
    if not title:
      title = rss_item.find('title').text
    description = source_class.get_story_description()
    if not description:
      description = rss_item.find('description').text
    author_name = source_class.get_story_author()
    publication_date = source_class.get_story_publication_date()
    body = source_class.get_story_body()

    author = None
    if author_name:
      author_name = author_name.strip()
      author = get_author_by_name(author_name)

    if not author:
      if author_name:
        author_name = author_name.strip()
        author = author_types.Author(name=author_name, affiliation=[source])
      else:
        author = author_types.Author(name=source.name, affiliation=[source])

    # extract Entities and Keywords from Title and Body
    entities = []
    keywords = []
    if title:
      title_entities, title_keywords = get_entities_and_keywords(title)
      entities.extend(title_entities)
      keywords.extend(title_keywords)
    if body:
      body_entities, body_keywords = get_entities_and_keywords(body)
      entities.extend(body_entities)
      keywords.extend(body_keywords)

    entities_dict = {}
    for entity in entities:
      if entity.entity.links in entities_dict:
        entities_dict[entity.entity.links].frequency += entity.frequency
      else:
        entities_dict.update({entity.entity.links: entity})
    keywords_dict = {}
    for keyword in keywords:
      if keyword.keyword.text in keywords_dict:
        keywords_dict[keyword.keyword.text].frequency += keyword.frequency
      else:
        keywords_dict.update({keyword.keyword.text: keyword})

    #Format image to list
    media_list = []
    if image_url:
      media_list.append(image_url)
    #make sure there is a summary
    if not description and body and len(body) > 280:
      description = body[0:280] + "..."

    #published_at is saved without timezone
    try:
      time = parser.parse(publication_date)
      publication_date = time.replace(tzinfo=None)
    except Exception:
      try:
        time = parser.parse(rss_item.find('pubdate').text)
        publication_date = time.replace(tzinfo=None)
      except Exception:
        publication_date = datetime.now()

    return story_types.Story(title=title,
                             body=body,
                             summary=description,
                             source=source,
                             author=author,
                             entities=list(entities_dict.values()),
                             keywords=list(keywords_dict.values()),
                             images=media_list,
                             language=source.language,
                             published_at=publication_date,
                             url=article_url)

  except Exception:
    message_to_log = traceback.format_exc()
    tracing.log(current_module, 'exception', message_to_log)
    return None
