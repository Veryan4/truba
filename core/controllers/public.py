from fastapi import APIRouter, HTTPException, status
from typing import Tuple

from services.story import story
from services.user import user, auth
import project_types

router = APIRouter()


@router.get('/news/{language}',
            response_model=Tuple[project_types.ShortStory, ...])
def get_public_stories(language: str):
  return story.get_public_stories(language)


@router.post('/users')
def init_user(create_user: user.CreateUser):
  current_user = user.add_user(create_user)
  if type(current_user) == str:
    raise HTTPException(status_code=400, detail=user)
  auth.confirm_email_address(current_user.email)
  access_token = auth.create_access_token(data={"sub": current_user.user_id})
  return {"token": access_token, "user": current_user.dict()}


@router.post('/forgot_password')
def forgot_password(forgot_password_request: auth.ForgotPasswordRequest):
  result = auth.forgot_password(forgot_password_request.email)
  return {'result': result}


@router.post('/reset_password')
def reset_password(reset_password_token: auth.ResetPasswordRequest):
  current_user = auth.reset_password(reset_password_token.token,
                                     reset_password_token.new_password)
  if type(current_user) == str:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=current_user,
        headers={"WWW-Authenticate": "Bearer"},
    )
  access_token = auth.create_access_token(data={"sub": current_user.user_id})
  return {"token": access_token, "user": current_user.dict()}


@router.get('/unsubscribe/{user_email}')
def unsubscribe_email(user_email: str):
  result = user.unsubscribe_user_email(user_email)
  return {"result": result}
