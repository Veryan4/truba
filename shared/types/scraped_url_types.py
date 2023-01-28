from pydantic import BaseModel
from datetime import datetime


class ScrapedUrl(BaseModel):
  published_at: datetime = None
  source_name: str = None
  url: str = None
