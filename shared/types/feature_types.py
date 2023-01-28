from pydantic import BaseModel


class SolrFeatures(BaseModel):
  tfidf_sim_title: float = 0.0
  bm25_sim_title: float = 0.0
  tfidf_sim_body: float = 0.0
  bm25_sim_body: float = 0.0
  documentRecency: float = 0.0
  tfidf_sim_keywords: float = 0.0
  bm25_sim_keywords: float = 0.0
  tfidf_sim_entities: float = 0.0
  bm25_sim_entities: float = 0.0


class RankingFeatures(BaseModel):
  story_title: str = None
  source_alexa_rank: int = 0
  read_count: int = 0  # score for all Users
  shared_count: int = 0  # score for all Users
  angry_count: int = 0  # score for all Users
  cry_count: int = 0  # score for all Users
  neutral_count: int = 0  # score for all Users
  smile_count: int = 0  # score for all Users
  happy_count: int = 0  # score for all Users
  source_id: str = ""
  author_id:str = ""
  most_frequent_keyword: str = ""
  most_frequent_entity: str = ""
