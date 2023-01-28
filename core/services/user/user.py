from pydantic import BaseModel, Field
from passlib.context import CryptContext
from typing import Optional, Tuple
from datetime import datetime
import uuid

from services import mongo
from services.user import email
from shared import bson_id

DB_COLLECTION_NAME = "User"


class User(BaseModel):
  id: bson_id.ObjectIdStr = Field(None, alias="_id")
  user_id: str = ""
  username: str
  email: str
  disabled: Optional[bool] = None
  language: str = "en"
  is_admin: bool = False
  is_personalized: bool = False
  has_personalization: bool = False
  rated_count: int = 0
  terms_consent: Optional[str] = None
  subscription: Optional[dict] = None
  is_email_subscribed: bool = False


class SecretUser(User):
  hashed_password: str
  reset_password_bytes: Optional[str] = None


class CreateUser(BaseModel):
  username: str
  email: str
  password: str
  terms_consent: str
  language: str = "en"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def add_user(create_user: CreateUser):
  """Creates a user in the db, given the email address provided isn't
  already in use.

    Args:
        user_id: The user's id for which stories have been read.

    Returns:
        The User object of the created user. If there was an issue with the user
        creation a string is returned.

    """

  mongo_filter = {"email": create_user.email}
  current_users = mongo.get(DB_COLLECTION_NAME, mongo_filter)
  user_emails = tuple(x["email"] for x in current_users)
  if create_user.email not in user_emails:
    user = {
        "user_id": str(uuid.uuid4()),
        "username": create_user.username,
        "email": create_user.email,
        "hashed_password": pwd_context.hash(create_user.password),
        "terms_consent": create_user.terms_consent
    }
    result = mongo.add_or_update(user, DB_COLLECTION_NAME)
    if result:
      email.send_user_init_email(create_user.email)
      return User(**user)
    return "Failed to create User"
  return "User already exists"


def find_or_create(user_email: str, username: str):
  """Attempts to find a user with a given email address. If not found,
  it will create a user in Mongo and return it.

    Args:
        user_email: Email of the user.
        username: Username of the user.

    Returns:
        The User object of the found or created user. If there was an issue
        with the user creation a string is returned.

    """

  mongo_filter = {"email": user_email}
  current_users = mongo.get(DB_COLLECTION_NAME, mongo_filter, 1)
  if current_users:
    return User(**current_users[0])
  uid = str(uuid.uuid4())
  user = {
      "user_id": uid,
      "username": username,
      "email": user_email,
      "hashed_password": pwd_context.hash(uid),
      "terms_consent": datetime.now().isoformat()
  }
  result = mongo.add_or_update(user, DB_COLLECTION_NAME)
  if result:
    email.send_user_init_email(user_email)
    return User(**user)
  return "Failed to create User"


def update(user: User):
  """Updates the user in mongo.

    Args:
        user: The provided modified user object.

    Returns:
        The User object of the updated user. If there was an issue updating
        the user a string is returned.

    """

  mongo_filter = {"user_id": user.user_id}
  current_users = mongo.get(DB_COLLECTION_NAME, mongo_filter, 1)
  if current_users:
    user_dict = user.dict()
    user_dict.pop("_id", None)
    user_dict.pop("id", None)
    current_user = current_users[0] | user_dict
    result = mongo.add_or_update(current_user, DB_COLLECTION_NAME)
    if result:
      return User(**current_user)
    return "Failed to update User"
  return "User not found"


def get_ids():
  """Retrieves the list of all user_ids

    Returns:
        The list of all user ids.

    """

  return mongo.get(DB_COLLECTION_NAME, {}, distinct="user_id")


def get_emails(language: str) -> Tuple[dict, ...]:
  """Retrieves the list of all user emails for a given language.
    Filtered by user email preferences.

    Args:
        language: The user's preferred language.

    Returns:
        The list of all user emails for a given language.

    """

  mongo_filter = {"language": language, "is_email_subscribed": True}
  users = mongo.get(DB_COLLECTION_NAME, mongo_filter)
  if users:
    return tuple(user["email"] for user in users
                 if "email" in user and user["email"])
  return None


def get_subscriptions(language: str) -> Tuple[dict, ...]:
  """Retrieves the list of all user push notification subscriptions for a
  given language.

    Args:
        language: The user's preferred language.

    Returns:
        The list of all user push notification subscriptions for a
        given language.

    """

  mongo_filter = {"language": language}
  users = mongo.get(DB_COLLECTION_NAME, mongo_filter)
  if users:
    return tuple(user["subscription"] for user in users
                 if "subscription" in user and user["subscription"])
  return None


def get_by_id(user_id: str) -> Optional[User]:
  """Retrieves a User from the database given their id.

    Args:
        user_id: The id of the user.

    Returns:
        The User if found, otherwise None.

    """

  mongo_filter = {"user_id": user_id}
  users = mongo.get(DB_COLLECTION_NAME, mongo_filter, 1)
  if users:
    return User(**users[0])
  return None


def get_user_dict_by_email(user_email: str) -> Optional[dict]:
  """Retrieves a User in dict form from the database given their email.

    Args:
        user_email: The email of the user.

    Returns:
        The user dict if found, otherwise None.

    """

  mongo_filter = {"email": user_email}
  users = mongo.get(DB_COLLECTION_NAME, mongo_filter, 1)
  if users:
    return users[0]
  return None


def unsubscribe_user_email(user_email: str) -> Optional[bool]:
  """Unsubscribe the user from receiving the Daily Snap emails.

    Args:
        user_id: The email of the user.

    Returns:
        True is user's preference update was successful, False if not.
    """

  user_dict = get_user_dict_by_email(user_email)
  if user_dict:
    user = User(**user_dict)
    user.is_email_subscribed = False
    result = mongo.add_or_update(user.dict(), DB_COLLECTION_NAME)
    if result:
      return True
  return False


def update_reset_password_token(user_dict: dict, random_bytes: str):
  """Updates the stored user object with random bytes which are used
  for resetting a password.

    Args:
        user_dict: The dict form of the user object.
        random_bytes: A random assembly of bytes which will temporarily
          identify the user.

    Returns:
        The updated user object. If there was an issue updating the user a
        string is returned.

    """

  user_dict.update({"reset_password_bytes": random_bytes})
  result = mongo.add_or_update(user_dict, DB_COLLECTION_NAME)
  if result:
    return User(**user_dict)
  return "Failed to update User reset token"


def reset_password_by_token(random_bytes: str,
                            password: str) -> Optional[User]:
  """Updates the user's password by identifying with the random bytes.

    Args:
        random_bytes: A random assembly of bytes which will temporarily
          identify the user.
        password: The user's newly provided password to update.

    Returns:
        The updated user object. If there was an issue updating the user a
        string is returned.

    """

  mongo_filter = {"reset_password_bytes": random_bytes}
  users = mongo.get(DB_COLLECTION_NAME, mongo_filter, 1)
  if users:
    user_update = {
        "hashed_password": pwd_context.hash(password),
        "reset_password_bytes": ""
    }
    user = users[0] | user_update
    result = mongo.add_or_update(user, DB_COLLECTION_NAME)
    if result:
      return User(**user)
    return "Failed to update User password"
  return "Failed to find User via reset token"
