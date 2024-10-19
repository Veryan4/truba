import requests
import os
import logging
from dotenv import load_dotenv
from services import ranking

logger = logging.getLogger(__name__)


def get_user_ids():
  response = requests.get(os.getenv("CORE_URL") + "/user/ids")
  if response:
    user_ids = list(response.json())
    return user_ids
  return None


def get_features(user_id: str):
  response = requests.get(os.getenv("CORE_URL") + "/training/" +
                          user_id)
  if response:
    data_entries = list(response.json())
    return data_entries
  return None


def train():
  user_ids = get_user_ids()
  master_data_entry_list = []
  for user_id in user_ids:
    data_entries = get_features(user_id)
    if data_entries:
      master_data_entry_list = master_data_entry_list + data_entries
  if master_data_entry_list:
    result = ranking.train_ranking_model(master_data_entry_list)
    logger.info(result)
  else:
    logger.error("Failed to receive Feature list")


# Call Train() when file is called
if __name__ == '__main__':
  load_dotenv()
  train()
