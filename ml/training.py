import requests
import os
import logging
from dotenv import load_dotenv
from services import ranking

logger = logging.getLogger(__name__)


def get_features():
  response = requests.get(os.getenv("CORE_URL") + "/training")
  if response:
    data_entries = list(response.json())
    return data_entries
  return None


def train():
  data_list = get_features()
  if data_list:
    result = ranking.train_ranking_model(data_list)
    logger.info(result)
  else:
    logger.error("Failed to receive Feature list")


# Call Train() when file is called
if __name__ == '__main__':
  load_dotenv()
  train()
