from pydantic import BaseModel


class RankingData(BaseModel):
  story_id: str
  user_id: str = ""
  relevancy_rate: float = 0.0
  time_stamp: float = 0.0
  story_title: str = ""
  source_alexa_rank: int = 0
  read_count: int = 0
  shared_count: int = 0
  angry_count: int = 0
  cry_count: int = 0
  neutral_count: int = 0
  smile_count: int = 0
  happy_count: int = 0
  source_id: str = ""
  author_id:str = ""
  most_frequent_keyword: str = ""
  most_frequent_entity: str = ""
