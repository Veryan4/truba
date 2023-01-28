from pydantic import BaseModel, Field

from typing import List
from datetime import datetime
from uuid import UUID, uuid4
from shared import bson_id
from shared.types import source_types, author_types, entity_types, keyword_types


class Story(BaseModel):
  id: bson_id.ObjectIdStr = Field(None, alias='_id')
  story_id: UUID = Field(default_factory=uuid4)
  title: str = None
  body: str = None
  summary: str = None
  source: source_types.Source = None
  author: author_types.Author = None
  entities: List[entity_types.EntityInStory] = []
  keywords: List[keyword_types.KeywordInStory] = []
  images: List[str] = None
  language: str = None
  published_at: datetime = None
  url: str = None
  read_count: int = 0
  shared_count: int = 0
  angry_count: int = 0
  cry_count: int = 0
  neutral_count: int = 0
  smile_count: int = 0
  happy_count: int = 0


class StoryInDb(BaseModel):
  id: bson_id.ObjectIdStr = Field(None, alias='_id')
  story_id: UUID = Field(default_factory=uuid4)
  title: str = None
  body: str = None
  summary: str = None
  source_id: str = None
  author_id: UUID = None
  entities: List[entity_types.EntityInStoryDB] = []
  keywords: List[keyword_types.KeywordInStoryDB] = []
  images: List[str] = None
  language: str = None
  published_at: datetime = None
  url: str = None
  read_count: int = 0
  shared_count: int = 0
  angry_count: int = 0
  cry_count: int = 0
  neutral_count: int = 0
  smile_count: int = 0
  happy_count: int = 0


def convert_story_to_story_in_db(story: Story) -> StoryInDb:
  author_id = None
  if story.author:
    author_id = story.author.author_id
  source_id = None
  if story.source:
    source_id = story.source.source_id
  keywords = []
  for keyword in story.keywords:
    keyword_dict = keyword.dict()
    keyword_dict.update({'text': keyword.keyword.text})
    keyword_dict.pop('keyword', None)
    keywords.append(keyword_dict)
  entities = []
  for entity in story.entities:
    entity_dict = entity.dict()
    entity_dict.update({'links': entity.entity.links})
    entity_dict.pop('entity', None)
    entities.append(entity_dict)
  return StoryInDb(id=story.id,
                   story_id=story.story_id,
                   title=story.title,
                   body=story.body,
                   summary=story.summary,
                   published_at=story.published_at,
                   author_id=author_id,
                   source_id=source_id,
                   url=story.url,
                   images=story.images,
                   language=story.language,
                   keywords=keywords,
                   entities=entities,
                   read_count=story.read_count,
                   shared_count=story.shared_count,
                   angry_count=story.angry_count,
                   cry_count=story.cry_count,
                   neutral_count=story.neutral_count,
                   smile_count=story.smile_count,
                   happy_count=story.happy_count)


class StoryInSolr(BaseModel):
  id: str
  StoryId: str
  Title: str
  Body: str
  Summary: str = None
  PublishedAt: str = None
  Author: str = None
  AuthorId: str = None
  Source: str = None
  SourceId: str = None
  StoryUrl: str
  Images: List[str] = None
  Language: str = None
  Keywords: List[str] = None
  Entities: List[str] = None
  EntityLinks: List[str] = None


def convert_story_to_story_in_solr(story: Story) -> StoryInSolr:
  author_name = None
  author_id = None
  if story.author:
    author_name = story.author.name
    author_id = str(story.author.author_id)
  source_name = None
  source_id = None
  if story.source:
    source_name = story.source.name
    source_id = str(story.source.source_id)
  return StoryInSolr(id=story.id,
                     StoryId=str(story.story_id),
                     Title=story.title,
                     Body=story.body,
                     Summary=story.summary,
                     PublishedAt=str(story.published_at),
                     Author=author_name,
                     AuthorId=author_id,
                     Source=source_name,
                     SourceId=source_id,
                     StoryUrl=story.url,
                     Images=story.images,
                     Language=story.language,
                     Keywords=[k.keyword.text for k in story.keywords],
                     Entities=[e.entity.text for e in story.entities],
                     EntityLinks=[e.entity.links for e in story.entities])


class ShortStory(BaseModel):
  story_id: str
  title: str
  summary: str = None
  published_at: datetime = None
  author: str = None
  author_id: str = None
  source: str = None
  source_id: str = None
  keywords: List[str] = None
  entities: List[str] = None
  entity_links: List[str] = None
  url: str
  image: str = None
  language: str = None


def solr_story_to_short_story(story: dict) -> ShortStory:
  if story['StoryId'][0]:
    story['story_id'] = story['StoryId'][0]
  if 'Author' in story and story['Author'][0]:
    story['author'] = story['Author'][0]
  if 'AuthorId' in story and story['AuthorId'][0]:
    story['author_id'] = story['AuthorId'][0]
  if story['Source'][0]:
    story['source'] = story['Source'][0]
  if 'SourceId' in story and story['SourceId'][0]:
    story['source_id'] = story['SourceId'][0]
  if story['Title'][0]:
    story['title'] = story['Title'][0]
  if 'Summary' in story and story['Summary'][0]:
    story['summary'] = story['Summary'][0]
  if story['Language'][0]:
    story['language'] = story['Language'][0]
  if 'Images' in story and story['Images'][0]:
    story['image'] = story['Images'][0]
  if story['StoryUrl'][0]:
    story['url'] = story['StoryUrl'][0]
  return ShortStory(**story)


def convert_story_to_short_story(story: Story) -> ShortStory:
  author_name = None
  author_id = None
  if story.author:
    author_name = story.author.name
    author_id = str(story.author.author_id)
  source_name = None
  source_id = None
  if story.source:
    source_name = story.source.name
    source_id = str(story.source.source_id)
  images = None
  if story.images:
    images = story.images[0]
  return ShortStory(story_id=str(story.story_id),
                    title=story.title,
                    summary=story.summary,
                    published_at=story.published_at,
                    author=author_name,
                    author_id=author_id,
                    source=source_name,
                    source_id=source_id,
                    keywords=[k.keyword.text for k in story.keywords],
                    entities=[e.entity.text for e in story.entities],
                    entity_links=[e.entity.links for e in story.entities],
                    url=story.url,
                    image=images,
                    language=story.language)


def mock_story() -> Story:
  story = Story(id='',
               story_id=UUID('3d925894-7c07-4d70-be56-09f8e1f1071c'),
               title='A turtle is on the loose',
               body='Was there a hare chasing it?',
               summary='Nope it was just a green rock.',
               source=source_types.mock_source(),
               author=author_types.mock_author(),
               entities=[entity_types.mock_entity_in_story()],
               keywords=[keyword_types.mock_keyword_in_story()],
               images=[''],
               language='en',
               published_at=datetime(2021, 4, 4, 8, 0, 0, 0),
               url='https://bbc.com/news-story',
               read_count=0,
               shared_count=0,
               angry_count=0,
               cry_count=0,
               neutral_count=0,
               smile_count=0,
               happy_count=0)
  return story
