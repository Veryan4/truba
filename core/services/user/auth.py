from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, status, Query, WebSocket
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from google.oauth2 import id_token
import cachecontrol
import google.auth.transport.requests
import os
import requests

from services.user import user, email
from shared import setup

RESET_PASSWORD_TOKEN_EXPIRE_MINUTES = 15
ACCESS_TOKEN_EXPIRE_DAYS = 3
ENCRYPTION_ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
session = requests.session()
cached_session = cachecontrol.CacheControl(session)
request = google.auth.transport.requests.Request(session=cached_session)


class ForgotPasswordRequest(BaseModel):
  email: str


class ResetPasswordRequest(BaseModel):
  token: str
  new_password: str


def authenticate_user(email_address: str,
                      password: str) -> Union[user.User, bool]:
  """Verifies is the user should have access to his account by
  comparing the provided password to the hashed password stored in Mongo.

    Args:
        email: The user's provided email.
        password: The user's provided password.

    Returns:
        A User object is returned is validation is successful,
        otherwise False is returned.
    """

  user_dict = user.get_user_dict_by_email(email_address)
  if not user_dict:
    return False
  secret_user = user.SecretUser(**user_dict)
  if not secret_user:
    return False
  if not pwd_context.verify(password, secret_user.hashed_password):
    return False
  return user.User(**user_dict)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
  """Creates a JWT access token which will be used by the user to authenticate
  API calls instead of using a password.

    Args:
        data: A dict which contains information used to validated the user
        expires_delta: If provided the timedelta will be used for a custom
          expiry period.

    Returns:
        An encoded JWT access token. If no expires_delta was provided,
        the standard access token expiry period will be used.
    """

  to_encode = data.copy()
  if expires_delta:
    expire = datetime.utcnow() + expires_delta
  else:
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode,
                           os.getenv("JWT_SECRET"),
                           algorithm=ENCRYPTION_ALGORITHM)
  return encoded_jwt


def google_token_check(token: str = Depends(oauth2_scheme)):
  """Decodes a token provided by Google OAuth2, then returns the User
  object if it exists, otherwise it will create a new one.

    Args:
        token: The google OAuth2 token retrieved from the header.

    Returns:
        A User object associated with the email found in the token.
    """

  decoded_token = id_token.verify_oauth2_token(token, request,
                                               os.getenv("GOOGLE_CLIENT_ID"))
  return user.find_or_create(decoded_token["email"], decoded_token["name"])


async def get_current_user(token: str = Depends(oauth2_scheme)):
  """Decodes a token, then returns the User associated with said token.

    Args:
        token: The OAuth2 token retrieved from the header.

    Returns:
        A User object associated with the user_id found in the token.

    Raises:
        HTTPException: A 401 exception is raised if either the token can't be
        decoded or no User was found with the user_id found in the token.

    """

  credentials_exception = HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Could not validate credentials",
      headers={"WWW-Authenticate": "Bearer"},
  )
  try:
    payload = jwt.decode(token,
                         os.getenv("JWT_SECRET"),
                         algorithms=[ENCRYPTION_ALGORITHM])
    user_id: str = payload.get("sub")
    if user_id is None:
      raise credentials_exception
  except JWTError:
    raise credentials_exception
  current_user = user.get_by_id(user_id)
  if current_user is None:
    raise credentials_exception
  return current_user


async def get_current_active_user(
    current_user: user.User = Depends(get_current_user)):
  """Checks if the user is disabled.

    Args:
        current_user: The OAuth2 token retrieved from the header.

    Returns:
        The current_user provided by the argument.

    Raises:
        HTTPException: A 400 exception is raised if the user has been tagged
        as disabled.

    """

  if current_user.disabled:
    raise HTTPException(status_code=400, detail="Inactive user")
  return current_user


async def get_current_user_id(token: str = Depends(oauth2_scheme)):
  """Decodes a token, then returns the user_id found in said token.

    Args:
        token: The OAuth2 token retrieved from the header.

    Returns:
        The user_id found in the token.
    
    Raises:
        HTTPException: A 401 exception is raised if either the token can't be decoded 
        or no user_id was found in said token.

    """

  credentials_exception = HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Could not validate credentials",
      headers={"WWW-Authenticate": "Bearer"},
  )
  try:
    payload = jwt.decode(token,
                         os.getenv("JWT_SECRET"),
                         algorithms=[ENCRYPTION_ALGORITHM])
    user_id: str = payload.get("sub")
    if user_id is None:
      raise credentials_exception
  except JWTError:
    raise credentials_exception
  return user_id


def forgot_password(user_email: str):
  """Sends an email to the user with a token of random bytes that can be
  used to reset their password.

    Args:
        user_email: The email address provided by the user.

    Returns:
        If a user associated with the emails is found, returns the result
        of the sending email operation. Otherwise None is returned.

    """

  user_dict = user.get_user_dict_by_email(user_email)
  if not user_dict:
    return None
  reset_password_token_expires = timedelta(
      minutes=RESET_PASSWORD_TOKEN_EXPIRE_MINUTES)
  random_byte_count = 20
  random_bytes = bytes(os.urandom(random_byte_count)).hex()
  reset_password_token = create_access_token(
      data={"sub": random_bytes}, expires_delta=reset_password_token_expires)
  current_user = user.update_reset_password_token(user_dict, random_bytes)
  if type(current_user) == str:
    return current_user
  url = setup.get_client_domain_name(
  ) + "/password?token=" + reset_password_token
  return email.send_forgot_password_email(current_user.email, url)


def get_reset_token(token: str):
  """Decodes the reset password token.

    Args:
        token: The reset password token.

    Returns:
        The decoded random bytes content of the reset password token.

    Raises:
        HTTPException: A 401 exception is raised if either the token can't
        be decoded or no random bytes were found in said token.

    """

  credentials_exception = HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Could not validate reset password token",
      headers={"WWW-Authenticate": "Bearer"},
  )
  try:
    payload = jwt.decode(token,
                         os.getenv("JWT_SECRET"),
                         algorithms=[ENCRYPTION_ALGORITHM])
    reset_token: str = payload.get("sub")
    if reset_token is None:
      raise credentials_exception
  except JWTError:
    raise credentials_exception
  return reset_token


def reset_password(token: str, new_password: str):
  """Uses the random bytes found in the token to authenticate the user
  and reset their password.

    Args:
        token: The reset password token.
        new_password: The new password provided by the user.

    Returns:
        The result of the sending a success email is returned id successful.
        Otherwise a string indicating an error if the password reset failed.

    """

  random_bytes = get_reset_token(token)
  current_user = user.reset_password_by_token(random_bytes, new_password)
  if type(current_user) == str:
    return current_user
  return email.send_reset_password_email(current_user.email)


async def get_websocket_token(
    websocket: WebSocket,
    token: Union[str, None] = Query(default=None)):
  """Validates the access token found in the websocket connection,
  to make sure user should have access to the socket. The websocket connection
  is closed if the validation fails.

    Args:
        websocket: The websocket connection.
        sec_websocket_protocol: The header used to store the access token.

    Returns:
        The user id found in the websocket's token if valid. Otherwise None.

    """

  try:
    payload = jwt.decode(token,
                         os.getenv("JWT_SECRET"),
                         algorithms=[ENCRYPTION_ALGORITHM])
    user_id: str = payload.get("sub")
    if token is None or user_id is None:
      await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=status.WS_1008_POLICY_VIOLATION)
      return None
  except JWTError:
    await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=status.WS_1008_POLICY_VIOLATION)
    return None
  return user_id
