from datetime import datetime
from uuid import UUID

import project_types

def mock_story() -> project_types.Story:
  story = project_types.Story(id='',
               story_id=UUID('3d925894-7c07-4d70-be56-09f8e1f1071c'),
               title='A turtle is on the loose',
               body='Was there a hare chasing it?',
               summary='Nope it was just a green rock.',
               source=mock_source(),
               author=mock_author(),
               entities=[mock_entity_in_story()],
               keywords=[mock_keyword_in_story()],
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

def mock_author() -> project_types.Author:
  return project_types.Author(id="0912309120923",
                author_id=UUID("3d925894-7c07-4d70-be56-09f8e1f1071c"),
                name="Tom Lundy",
                affiliation=[mock_source()],
                reputation=0.0)

def mock_entity() -> project_types.Entity:
  return project_types.Entity(id="9876456345", text="Apple", type="ORG", links="AppleORG")


def mock_entity_in_story() -> project_types.EntityInStory:
  t = project_types.EntityInStory(entity=mock_entity(), frequency=0)
  return t

def mock_keyword() -> project_types.Keyword:
  return project_types.Keyword(id="9876456345", text="Apple", language="en")


def mock_keyword_in_story() -> project_types.KeywordInStory:
  return project_types.KeywordInStory(keyword=mock_keyword(), frequency=0)

def mock_source() -> project_types.Source:
  return project_types.Source(id="0928309128",
                source_id="EN-1",
                name="BBC",
                home_page_url="",
                rank_in_alexa=1048,
                language="en",
                rss_feed="",
                reputation=0.0)