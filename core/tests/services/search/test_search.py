from pytest_mock import MockerFixture

from services.search import search
from services.search import solr
from services.story import story
from tests import mocks
import project_types


def test_simple_search(mocker: MockerFixture):
  spy = mocker.patch('services.search.search.solr.generic_search',
                     return_value=[mock_story_in_solr().dict()])
  mocker.patch('services.search.search.solr_story_to_short_story',
               return_value=mock_short_story())

  assert search.simple_search(mock_search_query()) == [mock_short_story()]

  spy.assert_called_once_with(mock_search_query())


def test_solr_search_with_personalization(mocker: MockerFixture):
  spy = mocker.patch('services.search.search.solr.generic_search',
                     return_value=[mock_story_in_solr().dict()])
  mocker.patch('services.search.search.solr_story_to_short_story',
               return_value=mock_short_story())

  assert search.solr_search_with_personalization(
      mock_search_query()) == [mock_short_story()]

  spy.assert_called_once_with(mock_search_query())


def test_get_stories_for_training(mocker: MockerFixture):
  features = "tfidf_sim_title=0.0,bm25_sim_title=0.0,tfidf_sim_body=0.0"
  story_in_solr = mock_story_in_solr().dict()
  story_in_solr.update({"[features]": features})
  spy_search = mocker.patch('services.search.search.solr.generic_search',
                            return_value=[story_in_solr])
  spy_features = mocker.patch(
      'services.search.search.features.extract_solr_features',
      return_value=project_types.SolrFeatures())
  spy_story = mocker.patch('services.search.search.story.get_by_id',
                           return_value=mocks.mock_story())
  spy_ranking = mocker.patch(
      'services.search.search.features.extract_ranking_features',
      return_value=project_types.RankingFeatures())
  mocker.patch('services.search.search.solr_story_to_short_story',
               return_value=mock_short_story())

  assert search.get_stories_for_training(
      [str(mocks.mock_story().story_id)], "spoon",
      str(mocks.mock_story().story_id)) == [mock_story_with_features()]

  query = project_types.SearchQuery(
      story_id_list=[str(mocks.mock_story().story_id)],
      terms="spoon",
      user_id=str(mocks.mock_story().story_id),
      count=1,
      start_date=10,
      grouped="",
      sort="")
  query.learn_to_rank_params = project_types.LtrParams(model_name=str(
      mocks.mock_story().story_id),
                                                      params=[{
                                                          "efi.querytext":
                                                          "spoon"
                                                      }])
  spy_search.assert_called_once_with(query)
  spy_features.assert_called_once_with(features)
  spy_story.assert_called_once_with(mock_short_story().story_id)
  spy_ranking.assert_called_once_with(mocks.mock_story())


def mock_story_in_solr() -> project_types.StoryInSolr:
  current_story = mocks.mock_story()
  current_story.id = "3928398292"
  return solr.convert_story_to_story_in_solr(current_story)


def mock_short_story() -> project_types.ShortStory:
  s = mocks.mock_story()
  s.id = "3928398292"
  return story.convert_story_to_short_story(s)


def mock_story_with_features() -> project_types.StoryWithFeatures:
  return project_types.StoryWithFeatures(
      story=mock_short_story(),
      solr_features=project_types.SolrFeatures(),
      ranking_features=project_types.RankingFeatures())


def mock_search_query() -> project_types.SearchQuery:
  query = project_types.SearchQuery()
  query.learn_to_rank_params = project_types.LtrParams()
  return query
