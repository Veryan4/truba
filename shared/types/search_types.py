from pydantic import BaseModel
from typing import List, Dict
from shared.types import feature_types, story_types


class LtrParams(BaseModel):
  model_name: str = "defaultmodel"
  request_handler: str = "query"
  params: List[Dict[str, str]] = [{"efi.querytext": "*"}]
  fields: List[str] = ["*", "score", "[features]"]


class SearchQuery(BaseModel):
  terms: str = "*"
  user_id: str = None
  count: int = 24
  story_id_list: List[str] = []  # include StoryIds
  not_id_list: List[str] = []  # exclude StoryIds
  language: str = None
  start_date: int = 1  # number of days ago
  end_date: int = 0  # number of days ago
  source_names: List[str] = []
  author_names: List[str] = []
  learn_to_rank_params: LtrParams = None
  search_operator: int = 0
  grouped: str = 'Source'
  sort: str = 'PublishedAt desc'


class StoryWithFeatures(BaseModel):
  story: story_types.ShortStory
  solr_features: feature_types.SolrFeatures
  ranking_features: feature_types.RankingFeatures
