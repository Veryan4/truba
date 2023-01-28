from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Tuple

from services.search import search
from services.story import story
from services.user import user, personalization, auth, feedback, favorite
from services import redis
from shared.types import story_types, search_types

router = APIRouter()


@router.get("/users/me")
async def read_users_me(current_user: user.User = Depends(
    auth.get_current_active_user)):
  return {"user": current_user.dict()}


@router.put("/users")
def updating_user(current_user: user.User,
                  user_id: str = Depends(auth.get_current_user_id)):
  current_user.user_id = user_id
  updated_user = user.update(current_user)
  if type(updated_user) == str:
    raise HTTPException(status_code=400, detail=updated_user)
  return {"user": updated_user.dict()}


@router.get("/users/email")
async def confirm_email(current_user: user.User = Depends(
    auth.get_current_active_user)):
  current_user.is_email_subscribed = True
  user.update(current_user)
  return {"user": current_user.dict()}


@router.get("/google/{token}")
async def google_auth(token: str):
  current_user = auth.google_token_check(token)
  if type(current_user) == str:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=current_user,
        headers={"WWW-Authenticate": "Bearer"},
    )
  access_token = auth.create_access_token(data={"sub": current_user.user_id})
  return {"token": access_token, "user": current_user.dict()}


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()):
  current_user = auth.authenticate_user(form_data.username, form_data.password)
  if not current_user:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
  access_token = auth.create_access_token(data={"sub": current_user.user_id})
  return {"token": access_token, "user": current_user.dict()}


@router.get("/user/info/{language}",
            response_model=personalization.Personalization)
async def get_personalization_items(language: str,
                              user_id: str = Depends(
                                  auth.get_current_user_id)):
  return personalization.get_personalization(user_id, language)


@router.get("/recommended-news/{language}",
            response_model=Tuple[story_types.ShortStory, ...])
def get_recommended_stories(language: str,
                            user_id: str = Depends(auth.get_current_user_id)):
  return story.get_recommended_stories(user_id, language)


@router.post("/single-article/{language}",
             response_model=story_types.ShortStory)
def get_single_story(language: str,
                     not_id_list: List[str],
                     user_id: str = Depends(auth.get_current_user_id)):
  return story.get_single_story(not_id_list, language)


@router.post("/feedback")
def receive_feedback(user_feedback: feedback.UserFeedback,
                     user_id: str = Depends(auth.get_current_user_id)):
  user_feedback.user_id = user_id
  redis.worker_queue.enqueue(feedback.received, user_feedback)
  return {"job": "received Queued"}


@router.post("/source")
def update_from_user_source(fave: favorite.Favorite,
                            user_id: str = Depends(auth.get_current_user_id)):
  fave.user_id = user_id
  result = favorite.update_from_user(fave, "FavoriteSource")
  return {"result": result}


@router.post("/author")
def update_from_user_author(fave: favorite.Favorite,
                            user_id: str = Depends(auth.get_current_user_id)):
  fave.user_id = user_id
  result = favorite.update_from_user(fave, "FavoriteAuthor")
  return {"result": result}


@router.post("/keyword")
def update_from_user_keyword(fave: favorite.Favorite,
                             user_id: str = Depends(auth.get_current_user_id)):
  fave.user_id = user_id
  result = favorite.update_from_user(fave, "FavoriteKeyword")
  return {"result": result}


@router.post("/entity")
def update_from_user_entity(fave: favorite.Favorite,
                            user_id: str = Depends(auth.get_current_user_id)):
  fave.user_id = user_id
  result = favorite.update_from_user(fave, "FavoriteEntity")
  return {"result": result}


@router.post("/search", response_model=List[story_types.ShortStory])
def get_stories(search_query: search_types.SearchQuery,
                user_id: str = Depends(auth.get_current_user_id)):
  search_query.user_id = user_id
  return search.simple_search(search_query)


@router.post("/search/personalized",
             response_model=List[story_types.ShortStory])
def get_personalized_stories(search_query: search_types.SearchQuery,
                             user_id: str = Depends(auth.get_current_user_id)):
  search_query.user_id = user_id
  return search.solr_search_with_personalization(search_query)
