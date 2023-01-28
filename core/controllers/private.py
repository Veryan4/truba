from fastapi import APIRouter, HTTPException
from typing import List, Tuple

from services.search import solr
from services.story import story, source, author, scraped_url
from services.user import user, feedback
from services import redis
from shared.types import source_types, author_types, story_types, scraped_url_types, data_set_types, search_types

router = APIRouter()


@router.post('/stories')
def add_stories(stories: Tuple[story_types.Story, ...]):
  redis.worker_queue.enqueue(story.insert_stories, stories)
  return {'addStoriesJob': "Job Queued"}


@router.get('/scraped', response_model=Tuple[str, ...])
def get_scraped_urls(source_name: str):
  urls = scraped_url.get_by_source_name(source_name)
  if not urls:
    raise HTTPException(status_code=404, detail="Urls not found")
  return urls

@router.post('/scraped')
def add_scraped_urls(scrapped_urls: Tuple[scraped_url_types.ScrapedUrl, ...]):
  redis.worker_queue.enqueue(scraped_url.add_scraped_urls, scrapped_urls)
  return {'add_scraped_urls': "Job Queued"}


@router.get('/sources/{language}',
            response_model=Tuple[source_types.Source, ...])
def get_sources(language: str):
  sources = source.get_all_sources(language)
  if not sources:
    raise HTTPException(status_code=404, detail="Sources not found")
  return sources


@router.get('/sources/reset')
def reset_sources():
  source.reset_sources()
  return {'result': 'Sources Reset'}


@router.get('/authors/name', response_model=author_types.Author)
def get_author_by_name(author_name: str):
  current_author = author.get_by_name(author_name)
  if not current_author:
    raise HTTPException(status_code=404, detail="Author not found")
  return current_author


@router.get('/training/{user_id}',
            response_model=List[data_set_types.RankingData])
def get_training_feedbacks(user_id: str):
  result = feedback.get_tf_training_data(user_id)
  if not result:
    raise HTTPException(status_code=404, detail="No Training Data Found")
  return result


@router.delete('/training/{user_id}')
def delete_user_feedbacks(user_id: str):
  redis.worker_queue.enqueue(feedback.remove_feedback_of_user, user_id)
  return {'feedbackJob': "Job Queued"}


@router.get('/user/ids', response_model=Tuple[str, ...])
def get_user_ids():
  return user.get_ids()


@router.get('/user/subscriptions/{language}', response_model=Tuple[dict, ...])
def get_user_subscriptions(language: str):
  subscriptions = user.get_subscriptions(language)
  if not subscriptions:
    raise HTTPException(status_code=404, detail="No subscriptions Found")
  return subscriptions


@router.get('/news/{language}',
            response_model=Tuple[story_types.ShortStory, ...])
def get_public_stories(language: str):
  return story.get_public_stories(language)


@router.get('/update-index/{language}')
def update_ranking_index(language: str):
  return story.update_tf_index(language)


@router.get('/solr/features')
def get_solr_features(search_query: search_types.SearchQuery):
  return solr.generic_search(search_query)


@router.get('/solr/reset')
def get_solr_reset():
  redis.worker_queue.enqueue(solr.delete_all)
  redis.worker_queue.enqueue(solr.refill)
  return {'Refill Solr': "Job Queued"}
