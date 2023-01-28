from pytest_mock import MockerFixture

from services.search import search
from shared.types import search_types, story_types, feature_types


def test_simple_search(mocker: MockerFixture):
  spy = mocker.patch('services.search.search.solr.generic_search',
                     return_value=[mock_story_in_solr().dict()])
  mocker.patch('shared.types.story_types.solr_story_to_short_story',
               return_value=mock_short_story())

  assert search.simple_search(mock_search_query()) == [mock_short_story()]

  spy.assert_called_once_with(mock_search_query())


def test_solr_search_with_personalization(mocker: MockerFixture):
  spy = mocker.patch('services.search.search.solr.generic_search',
                     return_value=[mock_story_in_solr().dict()])
  mocker.patch('shared.types.story_types.solr_story_to_short_story',
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
      return_value=feature_types.SolrFeatures())
  spy_story = mocker.patch('services.search.search.story.get_by_id',
                           return_value=story_types.mock_story())
  spy_ranking = mocker.patch(
      'services.search.search.features.extract_ranking_features',
      return_value=feature_types.RankingFeatures())
  mocker.patch('shared.types.story_types.solr_story_to_short_story',
               return_value=mock_short_story())

  assert search.get_stories_for_training(
      [str(story_types.mock_story().story_id)], "spoon",
      str(story_types.mock_story().story_id)) == [mock_story_with_features()]

  query = search_types.SearchQuery(
      story_id_list=[str(story_types.mock_story().story_id)],
      terms="spoon",
      user_id=str(story_types.mock_story().story_id),
      count=1,
      start_date=10,
      grouped="",
      sort="")
  query.learn_to_rank_params = search_types.LtrParams(model_name=str(
      story_types.mock_story().story_id),
                                                      params=[{
                                                          "efi.querytext":
                                                          "spoon"
                                                      }])
  spy_search.assert_called_once_with(query)
  spy_features.assert_called_once_with(features)
  spy_story.assert_called_once_with(mock_short_story().story_id)
  spy_ranking.assert_called_once_with(story_types.mock_story())


def mock_story_in_solr() -> story_types.StoryInSolr:
  current_story = story_types.mock_story()
  current_story.id = "3928398292"
  return story_types.convert_story_to_story_in_solr(current_story)


def mock_short_story() -> story_types.ShortStory:
  story = story_types.mock_story()
  story.id = "3928398292"
  return story_types.convert_story_to_short_story(story)


def mock_story_with_features() -> search_types.StoryWithFeatures:
  return search_types.StoryWithFeatures(
      story=mock_short_story(),
      solr_features=feature_types.SolrFeatures(),
      ranking_features=feature_types.RankingFeatures())


def mock_search_query() -> search_types.SearchQuery:
  query = search_types.SearchQuery()
  query.learn_to_rank_params = search_types.LtrParams()
  return query
