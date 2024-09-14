import os
import pysolr
import requests
import json
from fastapi.encoders import jsonable_encoder
from datetime import datetime, timedelta

from services.user import user, personalization
from services import mongo
from shared import setup
import project_types

DAYS_OF_STORIES_IN_SOLR = 10
STORIES_PER_SOURCE = 90


def get_connection():
  """Retrieves the connection to the Solr database. Used for any queries.

    Returns:
        The connection to the Solr database.
    """

  solr_uri = "http://" + os.getenv("SOLR_HOSTNAME") + ":" + os.getenv(
      "SOLR_PORT") + "/solr/" + os.getenv("ENVIRONMENT")
  return pysolr.get_connection(solr_uri)


def get_operator(operator: int) -> str:
  """Returns the AND/OR operator given it's representative int.

    Args:
        operator: The number which represents the string of operator.

    Returns:
        "AND" if operator is 0, "OR" if operator is 1.
    """

  if operator == 0:
    return " AND "
  else:
    return " OR "


def generic_search(search_query: project_types.SearchQuery):
  """Translates the SearchQuery to a query Solr will understand,
  executes said query and returns the results.

    Args:
        search_query: The query that is used on the Solr index.

    Returns:
        A list of stories from Solr.
    """

  solr = get_connection()
  query_params = {}
  req_handler = "query"
  learn_to_rank_params = search_query.learn_to_rank_params
  if learn_to_rank_params.model_name:
    ltr_params = "{!ltr model=" + learn_to_rank_params.model_name
    for param in learn_to_rank_params.params:
      ltr_params += " "
      key = next(iter(param))
      ltr_params += key + "=" + param[key]
    ltr_params += "}"
    query_params.update({"rq": ltr_params})
    fields = ','.join(learn_to_rank_params.fields)
    if not learn_to_rank_params.fields:
      fields = "*"
    query_params.update({"fl": fields})
    req_handler = learn_to_rank_params.request_handler
  if search_query.sort:
    query_params.update({"sort": search_query.sort})
  query_params.update({"rows": str(search_query.count)})
  fq_params = []
  if search_query.start_date:
    fq_params.append('PublishedAt:[NOW-' + str(search_query.start_date) +
                     'DAY/DAY TO NOW-' + str(search_query.end_date) + 'DAY]')
  if search_query.language:
    fq_params.append('Language:' + search_query.language)
  if search_query.author_names:
    fq_params.append('Author:(' + ' OR '.join(search_query.author_names) + ')')
  if fq_params:
    query_params.update({"fq": fq_params})
  query_params.update({"qt": ("/" + req_handler)})
  #Group results based on Source
  if search_query.grouped:
    query_params.update({"group": "true"})
    query_params.update({"group.field": search_query.grouped})
  q = []
  if search_query.terms:
    if search_query.terms == "*":
      q.append("*:*")
    else:
      terms_list = search_query.terms.split()
      solr_operator = get_operator(search_query.search_operator)
      q.append("Body:(" + solr_operator.join(terms_list) + ")")
  if search_query.not_id_list:
    q.append('-StoryId:(' + ' OR '.join(search_query.not_id_list) + ')')
  if search_query.story_id_list:
    q.append('StoryId:(' + ' OR '.join(search_query.story_id_list) + ')')
  if search_query.source_names:
    q.append('Source:(' + ' OR '.join(search_query.source_names) + ')')
  query_string = " ".join(q)
  try:
    solr_result = solr.search(query_string, **query_params)
    return get_results_from_solr(solr_result, search_query.grouped)
  except pysolr.SolrError:
    reset()
    if learn_to_rank_params.model_name:
      personalization.add_solr_model(learn_to_rank_params.model_name)
    solr_result = solr.search(query_string, **query_params)
    return get_results_from_solr(solr_result, search_query.grouped)


def get_results_from_solr(solr_result, is_grouped: str):
  """Formats the search results from Solr.

    Args:
        solr_result: The raw search result from Solr.
        is_grouped: String used to group search results.
          An empty string will change the required formatting.

    Returns:
        A list of formatted solr stories.
    """

  if is_grouped:
    return [
        group["doclist"]["docs"][0]
        for group in solr_result.grouped['Source']['groups']
    ]
  return [result for result in solr_result]


def delete_all():
  """Empties the Solr index.
    """

  solr = get_connection()
  solr.delete(q='*:*')


def refill_stories(source_id: str) -> dict:
  """Fills the Solr index with n stories from the last n days from a
  given source.

    Args:
        source_id: The id of the source from which to get the stories
          from Mongo.

    Returns:
        A dictionary where the results of the update are separated per day.
    """

  result_dict = {}
  for day in range(0, DAYS_OF_STORIES_IN_SOLR):
    end_delta = timedelta(day - 1)
    end = datetime.utcnow() - end_delta
    start_delta = timedelta(1)
    start = end - start_delta
    mongo_filter = {
        "published_at": {
            '$gte': start,
            '$lt': end
        },
        "source.id": source_id
    }
    source_stories = mongo.get("Story", mongo_filter, limit=STORIES_PER_SOURCE)
    stories = [project_types.Story(**story) for story in source_stories]
    stories_in_solr = [
        convert_story_to_story_in_solr(s) for s in stories
    ]
    stories_to_push = [x.dict() for x in stories_in_solr if x is not None]
    result = get_connection().add(stories_to_push)
    result_dict.update({'Day_' + str(day): result})
  return result_dict


def refill() -> dict:
  """Fills the Solr with stories retrieved from Mongo for each source.

    Returns:
        A dictionary where the results of the update are separated per
        source and per day.
    """

  result_dict = {}
  sources = mongo.get("Source", {})
  for source in sources:
    result = refill_stories(str(source['_id']))
    result_dict.update({source['name'].replace(' ', '_') + '_Stories': result})
  return result_dict


def reset() -> dict:
  """Deletes the Solr index. Then updates the Solr configuration given
  static JSON files. Then refills the Solr index with stories retrieved
  from the Mongo database.

    Returns:
        The result dictionary from the solr.refill() function. 
    """

  delete_all()
  files = [
      'text_tfidf.json', 'querytext.json', 'published_at_delete.json',
      'published_at.json', 'title_tfidf.json', 'title_copy.json',
      'body_tfidf.json', 'body_copy.json', 'body_copy.json', 'keywords.json',
      'keywords_tfidf.json', 'keywords_copy.json', 'entities.json',
      'entities_tfidf.json', 'entities_copy.json'
  ]
  for json_file in files:
    with open('../data/solr_data/' + json_file) as json_file:
      payload = json.load(json_file)
      requests.post("http://" + os.getenv("SOLR_HOSTNAME") + ":" +
                    os.getenv("SOLR_PORT") + "/solr/" +
                    os.getenv("ENVIRONMENT") + "/schema",
                    json=payload)
  with open('../data/solr_data/efi_feature_store.json') as json_file:
    payload = json.load(json_file)
    requests.put("http://" + os.getenv("SOLR_HOSTNAME") + ":" +
                 os.getenv("SOLR_PORT") + "/solr/" + os.getenv("ENVIRONMENT") +
                 "/schema/feature-store",
                 json=payload)
  model_ids = user.get_ids()
  json_to_push = jsonable_encoder(model_ids)
  requests.post(setup.get_base_ml_service_url() + "/model-store/reset",
                json=json_to_push)
  return refill()

def convert_story_to_story_in_solr(story: project_types.Story) -> project_types.StoryInSolr:
  author_name = None
  author_id = None
  if story.author:
    author_name = story.author.name
    author_id = str(story.author.author_id)
  source_name = None
  source_id = None
  if story.source:
    source_name = story.source.name
    source_id = str(story.source.source_id)
  return project_types.StoryInSolr(id=story.id,
                     StoryId=str(story.story_id),
                     Title=story.title,
                     Body=story.body,
                     Summary=story.summary,
                     PublishedAt=str(story.published_at),
                     Author=author_name,
                     AuthorId=author_id,
                     Source=source_name,
                     SourceId=source_id,
                     StoryUrl=story.url,
                     Images=story.images,
                     Language=story.language,
                     Keywords=[k.keyword.text for k in story.keywords],
                     Entities=[e.entity.text for e in story.entities],
                     EntityLinks=[e.entity.links for e in story.entities])
