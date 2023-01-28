from pydantic import BaseModel, Field
from shared import bson_id


class Keyword(BaseModel):
  id: bson_id.ObjectIdStr = Field(None, alias="_id")
  text: str
  language: str = None


class KeywordInStory(BaseModel):
  keyword: Keyword
  frequency: int


class KeywordInStoryDB(BaseModel):
  text: str
  frequency: int


def mock_keyword() -> Keyword:
  return Keyword(id="9876456345", text="Apple", language="en")


def mock_keyword_in_story() -> KeywordInStory:
  return KeywordInStory(keyword=mock_keyword(), frequency=0)
