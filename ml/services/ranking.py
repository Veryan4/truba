from pydantic import BaseModel, Field
from typing import Dict, Text, Any
import requests
import logging
import pandas as pd
import numpy as np
from sklearn import model_selection, preprocessing
from sklearn.metrics import mean_squared_error
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

import os

from services import mongo
from classes import bson_id

logger = logging.getLogger(__name__)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

RANKING_MODEL_WEIGHTS_DIR = "ranking_models/my_model_weights"
RANKING_MODEL_DATASET_DIR = "ranking_models/dataset.parquet"
RANKING_MODEL_DIR = "ranking_models/model_scripted.pt"
LANGUAGES = ("en", "fr")
EPOCHS = 2
BATCH_SIZE = 32

class NewsRankingDataset(Dataset):

    def __init__(self, story_id,
      user_id, time_stamp, relevancy_rate, source_id, author_id,
      most_frequent_entity, most_frequent_keyword, source_alexa_rank,
      read_count, shared_count, angry_count, cry_count, happy_count, neutral_count, smile_count):

        self.story_id = story_id
        self.user_id = user_id
        self.time_stamp = time_stamp
        self.relevancy_rate = relevancy_rate
        self.source_id = source_id
        self.author_id = author_id
        self.most_frequent_entity = most_frequent_entity
        self.most_frequent_keyword = most_frequent_keyword
        self.source_alexa_rank = source_alexa_rank
        self.read_count = read_count
        self.shared_count = shared_count
        self.angry_count = angry_count
        self.cry_count = cry_count
        self.happy_count = happy_count
        self.neutral_count = neutral_count
        self.smile_count = smile_count

    def __len__(self):
        return len(self.story_id)

    def __getitem__(self, item):
        story_id = self.story_id[item]
        user_id = self.user_id[item]
        time_stamp = self.time_stamp[item]
        relevancy_rate = self.relevancy_rate[item]
        source_id = self.source_id[item]
        author_id = self.author_id[item]
        most_frequent_entity = self.most_frequent_entity[item]
        most_frequent_keyword = self.most_frequent_keyword[item]
        source_alexa_rank = self.source_alexa_rank[item]
        read_count = self.read_count[item]
        shared_count = self.shared_count[item]
        angry_count = self.angry_count[item]
        cry_count = self.cry_count[item]
        happy_count = self.happy_count[item]
        neutral_count = self.neutral_count[item]
        smile_count = self.smile_count[item]

        return {
            "story_id": torch.tensor(story_id, dtype=torch.long),
            "user_id": torch.tensor(user_id, dtype=torch.long),
            "time_stamp": torch.tensor(time_stamp, dtype=torch.long),
            "relevancy_rate": torch.tensor(relevancy_rate, dtype=torch.float),
            "source_id": torch.tensor(source_id, dtype=torch.long),
            "author_id": torch.tensor(author_id, dtype=torch.long),
            "most_frequent_entity": torch.tensor(most_frequent_entity, dtype=torch.long),
            "most_frequent_keyword": torch.tensor(most_frequent_keyword, dtype=torch.long),
            "source_alexa_rank": torch.tensor(source_alexa_rank, dtype=torch.long),
            "read_count": torch.tensor(read_count, dtype=torch.long),
            "shared_count": torch.tensor(shared_count, dtype=torch.long),
            "angry_count": torch.tensor(angry_count, dtype=torch.long),
            "cry_count": torch.tensor(cry_count, dtype=torch.long),
            "happy_count": torch.tensor(happy_count, dtype=torch.long),
            "neutral_count": torch.tensor(neutral_count, dtype=torch.long),
            "smile_count": torch.tensor(smile_count, dtype=torch.long),
        }

class NewsRecommendationModel(nn.Module):
    def __init__(
        self,
        num_users,
        num_stories,
        embedding_size=256,
        hidden_dim=256,
        dropout_rate=0.2,
    ):
        super(NewsRecommendationModel, self).__init__()
        self.num_users = num_users
        self.num_stories = num_stories
        self.embedding_size = embedding_size
        self.hidden_dim = hidden_dim

        self.user_embedding = nn.Embedding(
            num_embeddings=self.num_users, embedding_dim=self.embedding_size
        )
        self.story_embedding = nn.Embedding(
            num_embeddings=self.num_stories, embedding_dim=self.embedding_size
        )

        self.fc1 = nn.Linear(2 * self.embedding_size, self.hidden_dim)
        self.fc2 = nn.Linear(self.hidden_dim, 1)

        self.dropout = nn.Dropout(p=dropout_rate)

        self.relu = nn.ReLU()

    def forward(self, users, stories):
        user_embedded = self.user_embedding(users)
        story_embedded = self.story_embedding(stories)

        combined = torch.cat([user_embedded, story_embedded], dim=1)

        x = self.relu(self.fc1(combined))
        x = self.dropout(x)
        output = self.fc2(x)

        return output

def train_ranking_model(data_entries):
  data_frame = pd.DataFrame(data_entries)

  le_user = preprocessing.LabelEncoder()
  le_story = preprocessing.LabelEncoder()
  data_frame.user_id = le_user.fit_transform(data_frame.user_id.values)
  data_frame.story_id = le_story.fit_transform(data_frame.story_id.values)

  df_train, df_val = model_selection.train_test_split(
      data_frame, test_size=0.1, random_state=3, stratify=data_frame.relevancy_rate.values
  )

  train_dataset = NewsRankingDataset(
      user_id=df_train.user_id.values,
      story_id=df_train.story_id.values,
      relevancy_rate=df_train.relevancy_rate.values,
  )

  valid_dataset = NewsRankingDataset(
    user_id=df_train.user_id.values,
    story_id=df_train.story_id.values,
    relevancy_rate=df_train.relevancy_rate.values,
  )

  train_loader = DataLoader(
      train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=8
  )
  val_loader = DataLoader(
      valid_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=8
  )

  recommendation_model = NewsRecommendationModel(
      num_users=len(le_user.classes_),
      num_stories=len(le_story.classes_),
      embedding_size=64,
      hidden_dim=128,
      dropout_rate=0.1,
  ).to(device)

  optimizer = torch.optim.Adam(recommendation_model.parameters(), lr=1e-3)
  loss_func = nn.MSELoss()

  total_loss = 0
  log_progress_step = 100
  losses = []
  train_dataset_size = len(train_dataset)
  logger.info(f"Training on {train_dataset_size} samples...")

  recommendation_model.train()
  for e in range(EPOCHS):
      step_count = 0
      for i, train_data in enumerate(train_loader):
          output = recommendation_model(
              train_data["users"].to(device), train_data["movies"].to(device)
          )
          # Reshape the model output to match the target's shape
          output = output.squeeze()  # Removes the singleton dimension
          ratings = (
              train_data["ratings"].to(torch.float32).to(device)
          )  # Assuming ratings is already 1D

          loss = loss_func(output, ratings)
          total_loss += loss.sum().item()
          optimizer.zero_grad()
          loss.backward()
          optimizer.step()

          step_count += len(train_data["users"])

          if (
              step_count % log_progress_step == 0 or i == len(train_loader) - 1
          ):
              log_progress(
                  e, step_count, total_loss, log_progress_step, train_dataset_size, losses
              )
              total_loss = 0

  recommendation_model.eval()

  y_pred = []
  y_true = []
  with torch.no_grad():
      for i, valid_data in enumerate(val_loader):
          output = recommendation_model(
              valid_data["users"].to(device), valid_data["movies"].to(device)
          )
          ratings = valid_data["ratings"].to(device)
          y_pred.extend(output.cpu().numpy())
          y_true.extend(ratings.cpu().numpy())

  # Calculate RMSE
  rmse = mean_squared_error(y_true, y_pred, squared=False)
  should_save = save_ranking_model(recommendation_model, rmse)
  if should_save:
    return "Model improved with RMSE score: " + str(rmse)
  return "Model did not improve with RMSE score: " + str(rmse)

# Function to log progress
def log_progress(epoch, step, total_loss, log_progress_step, data_size, losses):

    avg_loss = total_loss / log_progress_step
    logger.info(
        f"\r{epoch+1:02d}/{EPOCHS:02d} | Step: {step}/{data_size} | Avg Loss: {avg_loss:<6.9f}"
    )
    losses.append(avg_loss)


class RankingModel(BaseModel):
  id: bson_id.ObjectIdStr = Field(None, alias="_id")
  ranking_model_id: str
  state_dict: dict
  rmse: float

def get_ranking_model():
  mongo_filter = {"ranking_model_id": "1"}
  ranking_models = mongo.get("RankingModel", mongo_filter, limit=1)
  if ranking_models:
    return RankingModel(**ranking_models[0])
  return None

def save_ranking_model(model, rmse: float):
  ranking_model = get_ranking_model()
  if not ranking_model:
    new_ranking_model = {
        "ranking_model_id": "1",
        "state_dict": model.state_dict(),
        "rmse": rmse
    }
    model_scripted = torch.jit.script(model)
    model_scripted.save(RANKING_MODEL_DIR)
    return mongo.add_or_update(new_ranking_model, "RankingModel")
  if rmse < ranking_model.rmse:  # The lower the RMSE metric, the more accurate our model is at predicting ranking
    ranking_model.state_dict = model.state_dict()
    ranking_model.rmse = rmse
    model_scripted = torch.jit.script(model)
    model_scripted.save(RANKING_MODEL_DIR)
    return mongo.add_or_update(ranking_model.dict(), "RankingModel")
  return None

def load_ranking_model():
  ranking_model = get_ranking_model()
  if ranking_model:
    model = torch.jit.load(RANKING_MODEL_DIR)
    model.eval()
    return model
  return None


def recommend_top_stories(model, user_id, data_frame, k=5, batch_size=100):
    model.eval()
    all_stories = data_frame['story_id'].unique().tolist()
    seen_stories = set(data_frame[data_frame['user_id'] == user_id]['story_id'].tolist())
    unseen_stories = [m for m in all_stories if m not in seen_stories]
    predictions = []

    with torch.no_grad():
        for i in range(0, len(unseen_stories), batch_size):
            batch_unseen_stories = unseen_stories[i:i+batch_size]
            user_tensor = torch.tensor([user_id] * len(batch_unseen_stories)).to(device)
            movie_tensor = torch.tensor(batch_unseen_stories).to(device)
            predicted_ratings = model(user_tensor, movie_tensor).view(-1).tolist()
            predictions.extend(zip(batch_unseen_stories, predicted_ratings))

    predictions.sort(key=lambda x: x[1], reverse=True)
    top_k_movies = [movie_id for movie_id, _ in predictions[:k]]
    return top_k_movies

def get_indexes():
  indexes = {}
  model = load_ranking_model()
  if not model:
    logger.error("Failed to load model index.")
    return None
  for language in LANGUAGES:
    response = requests.get(os.getenv("CORE_URL") +
                            "/update-index/" + language)
    if not response:
      logger.error("Failed to initialize " + language +
            " index. Update Index call failed")
      return None
    recent_stories = list(response.json())
    df = pd.DataFrame(recent_stories)
    dic = dict(df)
    if not dic:
      logger.error("Failed to initialize " + language + " index. There was no Data")
      return None
    dataset = tf.data.Dataset.from_tensor_slices(dic)

    story_ids = dataset.map(lambda x: x["story_id"]).shuffle(
        10_000, seed=42, reshuffle_each_iteration=False).batch(100)

    story_id_embeddings = story_ids.map(
            model.candidate_model.embedding_model._embeddings["story_id"])

    num_leaves = 100
    if len(recent_stories) < num_leaves:
      num_leaves = len(recent_stories)

    scann = tfrs.layers.factorized_top_k.ScaNN(model.query_model.embedding_model.user_embedding, num_reordering_candidates=1000, num_leaves=num_leaves)
    scann.index_from_dataset(
        tf.data.Dataset.zip((story_ids, story_id_embeddings)))
    indexes.update({language: scann})
  return indexes


def save_scann(model):
  scann = tfrs.layers.factorized_top_k.ScaNN(model.query_model.embedding_model.user_embedding, num_reordering_candidates=1000)
  tf.saved_model.save(
        scann,
        RANKING_MODEL_SCANN_DIR,
        options=tf.saved_model.SaveOptions(namespace_whitelist=["Scann"])
    )

def get_scann():
  return tf.saved_model.load(RANKING_MODEL_SCANN_DIR)
