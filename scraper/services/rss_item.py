from pydantic import BaseModel


class RssItem(BaseModel):
  pubdate: str = None
  title: str = None
  description: str = None
  url: str = None
