import requests
from services import ranking
from shared import tracing, setup

current_module = 'Training'


def get_user_ids():
  response = requests.get(setup.get_base_core_service_url() + "/user/ids")
  if response:
    user_ids = list(response.json())
    return user_ids
  return None


def get_features(user_id: str):
  response = requests.get(setup.get_base_core_service_url() + "/training/" +
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
    tracing.log(current_module, 'info', result)
  else:
    tracing.log(current_module, 'error', "Failed to receive Feature list")


# Call Train() when file is called
if __name__ == '__main__':
  train()
