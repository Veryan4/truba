from pytest_mock import MockerFixture

from services.search.search import features
from tests import mocks
import project_types


def test_extract_solr_features(mocker: MockerFixture):
  test_string = "tfidf_sim_title=0.0,bm25_sim_title=0.0,tfidf_sim_body=0.0"
  assert features.extract_solr_features(
      test_string) == project_types.SolrFeatures(tfidf_sim_title=0.0,
                                                 bm25_sim_title=0.0,
                                                 tfidf_sim_body=0.0)


def test_extract_ranking_features(mocker: MockerFixture):
  assert features.extract_ranking_features(
      mocks.mock_story()) == mock_ranking_features()


def mock_ranking_features() -> project_types.RankingFeatures:
  mock_story = mocks.mock_story()
  return project_types.RankingFeatures(story_title="A turtle is on the loose",
                                       source_alexa_rank=1048,
                                       read_count=0,
                                       shared_count=0,
                                       angry_count=0,
                                       cry_count=0,
                                       neutral_count=0,
                                       smile_count=0,
                                       happy_count=0,
                                       source_id=str(mock_story.source.source_id),
                                       author_id=str(mock_story.author.author_id),
                                       most_frequent_keyword="Apple",
                                       most_frequent_entity="AppleORG"
)
