from typing import List

from services.search import features, solr
from services.story import story
from services.user import read_story
import project_types


def simple_search(
    search_query: project_types.SearchQuery) -> List[project_types.ShortStory]:
  """Executes a generic search query on Solr

    Args:
        search_query: The query that used used for the Solr search.

    Returns:
        The list of stories returned from Solr, ordered by the most recent.
    """

  search_query.learn_to_rank_params = project_types.LtrParams(
      params=[{
          "efi.querytext": search_query.terms
      }])
  solr_result = solr.generic_search(search_query)
  list_stories = [
      solr_story_to_short_story(s) for s in solr_result
  ]
  list_stories = sorted(list_stories,
                        key=lambda story: story.published_at,
                        reverse=True)
  return list_stories


def solr_search_with_personalization(
    search_query: project_types.SearchQuery) -> List[project_types.ShortStory]:
  """Executes a search query on Solr with given personalization parameters.

    Args:
        search_query: The query that used used for the Solr search.

    Returns:
        The list of stories returned from Solr.
        Stories that have been previously read by the user are avoided.
    """

  model_name = "defaultmodel"
  if search_query.user_id:
    model_name = search_query.user_id
    read_story_ids = read_story.get_story_ids(search_query.user_id)
    if read_story_ids:
      search_query.not_id_list = list(read_story_ids)
  search_query.learn_to_rank_params = project_types.LtrParams(
      model_name=model_name, params=[{
          "efi.querytext": search_query.terms
      }])
  solr_result = solr.generic_search(search_query)
  return [solr_story_to_short_story(s) for s in solr_result]


def get_stories_for_training(
    story_ids: List[str], term: str,
    user_id: str) -> List[project_types.StoryWithFeatures]:
  """Retrieves stories from Solr with the associated features.
    This is used for the updating of the RankNet recommendation model.

    Args:
        story_ids: The stories to retrieve from the Solr index.
        term: The search term used for training.
        user_id: The id of the user used on the search.

    Returns:
        The list of stories returned from Solr and their associated features.
    """

  if term == "*":
    term = ""
  search_query = project_types.SearchQuery(story_id_list=story_ids,
                                          terms=term,
                                          user_id=user_id,
                                          count=len(story_ids),
                                          start_date=10,
                                          grouped="",
                                          sort="")
  model_name = "defaultmodel"
  if search_query.user_id:
    model_name = search_query.user_id
  search_query.learn_to_rank_params = project_types.LtrParams(
      model_name=model_name, params=[{
          "efi.querytext": search_query.terms
      }])
  solr_result = solr.generic_search(search_query)
  story_with_features_list = []
  for result in solr_result:
    solr_features = features.extract_solr_features(result["[features]"])
    short_story = solr_story_to_short_story(result)
    current_story = story.get_by_id(short_story.story_id)
    ranking_features = features.extract_ranking_features(current_story)
    story_with_features = project_types.StoryWithFeatures(
        story=short_story,
        solr_features=solr_features,
        ranking_features=ranking_features)
    story_with_features_list.append(story_with_features)
  return story_with_features_list


def solr_story_to_short_story(story: dict) -> project_types.ShortStory:
  if story['StoryId'][0]:
    story['story_id'] = story['StoryId'][0]
  if 'Author' in story and story['Author'][0]:
    story['author'] = story['Author'][0]
  if 'AuthorId' in story and story['AuthorId'][0]:
    story['author_id'] = story['AuthorId'][0]
  if story['Source'][0]:
    story['source'] = story['Source'][0]
  if 'SourceId' in story and story['SourceId'][0]:
    story['source_id'] = story['SourceId'][0]
  if story['Title'][0]:
    story['title'] = story['Title'][0]
  if 'Summary' in story and story['Summary'][0]:
    story['summary'] = story['Summary'][0]
  if story['Language'][0]:
    story['language'] = story['Language'][0]
  if 'Images' in story and story['Images'][0]:
    story['image'] = story['Images'][0]
  if story['StoryUrl'][0]:
    story['url'] = story['StoryUrl'][0]
  return project_types.ShortStory(**story)
