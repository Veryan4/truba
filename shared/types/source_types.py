from pydantic import BaseModel, Field
from shared import bson_id


class Source(BaseModel):
  id: bson_id.ObjectIdStr = Field(None, alias='_id')
  source_id: str
  name: str = None
  home_page_url: str = None
  rank_in_alexa: int = None
  language: str = None
  rss_feed: str = None
  reputation: float = 0.0


def mock_source() -> Source:
  return Source(id="0928309128",
                source_id="EN-1",
                name="BBC",
                home_page_url="",
                rank_in_alexa=1048,
                language="en",
                rss_feed="",
                reputation=0.0)
