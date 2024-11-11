from pydantic import BaseModel, Field
from typing import Dict, Text, Union, Sequence, Optional, Tuple
import requests
import logging
import pandas as pd
import numpy as np
import tensorflow as tf
import tensorflow_recommenders as tfrs
import os
import contextlib

from services import mongo
from classes import bson_id

logger = logging.getLogger(__name__)

RANKING_MODEL_WEIGHTS_DIR = "tf_models/my_model_weights"
RANKING_MODEL_DATASET_DIR = "tf_models/dataset.parquet"
RANKING_MODEL_SCANN_DIR = "tf_models/my_model_scann"
LANGUAGES = ("en", "fr")

def train_ranking_model(data_entries):
  data_frame = pd.DataFrame(data_entries)
  model = NewsRankingModel(data_entries=data_frame)
  model.compile(optimizer=tf.keras.optimizers.Adagrad(learning_rate=0.1))

  dataset_size = tf.data.experimental.cardinality(model.dataset).numpy()
  train_size = int(0.6 * dataset_size)
  test_size = int(0.4 * dataset_size)
  shuffled = model.dataset.shuffle(100_000,
                                   seed=42,
                                   reshuffle_each_iteration=False)
  train = shuffled.take(train_size)
  test = shuffled.skip(train_size).take(test_size)
  cached_train = train.shuffle(100_000).batch(8192).cache()
  cached_test = test.batch(4096).cache()

  model.fit(cached_train, epochs=3)
  eval_dict = model.evaluate(cached_test, return_dict=True)
  rmse = eval_dict["root_mean_squared_error"]
  result = save_ranking_model(model, eval_dict)
  if result:
    return "Model improved with RMSE score: " + str(rmse)
  return "Model did not improve with RMSE score: " + str(rmse)


class UserModel(tf.keras.Model):
  def __init__(self, embedding_dimension, unique_user_ids, timestamps,
               timestamp_buckets, **kwargs):
    super(UserModel, self).__init__(**kwargs)

    self.unique_user_ids = unique_user_ids

    self.user_embedding = tf.keras.Sequential([
        tf.keras.layers.StringLookup(
            vocabulary=self.unique_user_ids, mask_token=None),
        tf.keras.layers.Embedding(
            len(self.unique_user_ids) + 1, embedding_dimension),
    ])

    self.timestamp_buckets = timestamp_buckets

    self.timestamp_embedding = tf.keras.Sequential([
        tf.keras.layers.Discretization(
            self.timestamp_buckets),
        tf.keras.layers.Embedding(
            len(self.timestamp_buckets) + 1, embedding_dimension),
    ])
    self.normalized_timestamp = tf.keras.layers.Normalization(axis=None)

    self.normalized_timestamp.adapt(timestamps)

    self._embeddings = {}


  def call(self, features):
    embeddings = []
    embeddings.append(self.user_embedding(features["user_id"]))
    embeddings.append(self.timestamp_embedding(features["time_stamp"]))
    embeddings.append(tf.reshape(self.normalized_timestamp(features["time_stamp"]), (-1, 1)))
    return tf.concat(embeddings, axis=1)

  def get_config(self):
    config = {
        "user_embedding": self.user_embedding,
        "timestamp_embedding": self.timestamp_embedding,
        "normalized_timestamp": self.normalized_timestamp,
        "_embeddings": self._embeddings
    }
    return config

  @classmethod
  def from_config(cls, config):
    return cls(**config)


class NewsModel(tf.keras.Model):
  def __init__(self, embedding_dimension, string_features, int_features, **kwargs):
    super(NewsModel, self).__init__(**kwargs)

    self.string_feature_keys = [
        "story_id", "story_title", "source_id", "author_id",
        "most_frequent_keyword", "most_frequent_entity"
    ]

    self.int_feature_keys = [
        "source_alexa_rank", "read_count", "shared_count", "angry_count",
        "cry_count", "neutral_count", "smile_count", "happy_count"
    ]

    self._embeddings = {}

    for feature_name in self.string_feature_keys:
      vocab = string_features.batch(1_000_000).map(lambda x: x[feature_name])
      vocabulary = np.unique(np.concatenate(list(vocab)))
      self._embeddings[feature_name] = tf.keras.Sequential([
          tf.keras.layers.StringLookup(
              vocabulary=vocabulary, mask_token=None),
          tf.keras.layers.Embedding(len(vocabulary) + 1, embedding_dimension)
      ])

    for feature_name in self.int_feature_keys:
      vocab = int_features.batch(1_000_000).map(lambda x: x[feature_name])
      vocabulary = np.unique(np.concatenate(list(vocab)))
      self._embeddings[feature_name] = tf.keras.Sequential([
          tf.keras.layers.IntegerLookup(
              vocabulary=vocabulary, mask_token=None),
          tf.keras.layers.Embedding(len(vocabulary) + 1, embedding_dimension)
      ])

  def call(self, features):
    embeddings = []
    for feature_name in self.string_feature_keys:
      embedding_fn = self._embeddings[feature_name]
      embeddings.append(embedding_fn(features[feature_name]))
    for feature_name in self.int_feature_keys:
      embedding_fn = self._embeddings[feature_name]
      embeddings.append(embedding_fn(features[feature_name]))

    return tf.concat(embeddings, axis=1)

  def get_config(self):
    config = {
        "_embeddings": self._embeddings
    }
    return config

  @classmethod
  def from_config(cls, config):
    return cls(**config)


class QueryModel(tf.keras.Model):
  def __init__(self,
               layer_sizes,
               embedding_dimension,
               unique_user_ids,
               timestamps,
               timestamp_buckets,
               use_cross_layer=False,
               projection_dim=None,
               **kwargs):
    super(QueryModel, self).__init__(**kwargs)
    # We first use the user model for generating embeddings.
    self.embedding_model = UserModel(embedding_dimension, unique_user_ids,
                                     timestamps, timestamp_buckets)

    # Then construct the layers.
    self._deep_layers = [
        tf.keras.layers.Dense(layer_size, activation="relu")
        for layer_size in layer_sizes
    ]

    if use_cross_layer:
      self._cross_layer = tfrs.layers.dcn.Cross(
          projection_dim=projection_dim, kernel_initializer="glorot_uniform")
    else:
      self._cross_layer = None

    self._logit_layer = tf.keras.layers.Dense(1)

  def call(self, inputs):
    feature_embedding = self.embedding_model(inputs)
    # Build Cross Network
    if self._cross_layer is not None:
      feature_embedding = self._cross_layer(feature_embedding)

    # Build Deep Network
    for deep_layer in self._deep_layers:
      feature_embedding = deep_layer(feature_embedding)

    return self._logit_layer(feature_embedding)

  def get_config(self):
    config = {
        "embedding_model": self.embedding_model,
        "_deep_layers": self._deep_layers,
        "_cross_layer": self._cross_layer,
        "_logit_layer": self._logit_layer
    }
    return config

  @classmethod
  def from_config(cls, config):
    return cls(**config)


class CandidateModel(tf.keras.Model):
  def __init__(self,
               layer_sizes,
               embedding_dimension,
               string_features,
               int_features,
               use_cross_layer=False,
               projection_dim=None,
               **kwargs):
    super(CandidateModel, self).__init__(**kwargs)
    self.embedding_model = NewsModel(embedding_dimension,
                                     string_features,
                                     int_features)

    self._deep_layers = [
        tf.keras.layers.Dense(layer_size, activation="relu")
        for layer_size in layer_sizes
    ]

    if use_cross_layer:
      self._cross_layer = tfrs.layers.dcn.Cross(
          projection_dim=projection_dim, kernel_initializer="glorot_uniform")
    else:
      self._cross_layer = None

    self._logit_layer = tf.keras.layers.Dense(1)

  def call(self, inputs):
    feature_embedding = self.embedding_model(inputs)
    # Build Cross Network
    if self._cross_layer is not None:
      feature_embedding = self._cross_layer(feature_embedding)

    # Build Deep Network
    for deep_layer in self._deep_layers:
      feature_embedding = deep_layer(feature_embedding)

    return self._logit_layer(feature_embedding)

  def get_config(self):
    config = {
        "embedding_model": self.embedding_model,
        "_deep_layers": self._deep_layers,
        "_cross_layer": self._cross_layer,
        "_logit_layer": self._logit_layer
    }
    return config

  @classmethod
  def from_config(cls, config):
    return cls(**config)


class NewsRankingModel(tfrs.models.Model):
  def __init__(self,
               data_entries,
               ranking_weight: float = 1.0,
               retrieval_weight: float = 1.0,
               layer_sizes=[32],
               embedding_dimension=32,
               **kwargs):
    super(NewsRankingModel, self).__init__(**kwargs)
    self.data_entries = data_entries

    tf.random.set_seed(42)

    self.dataset = tf.data.Dataset.from_tensor_slices(pd.DataFrame.from_dict(self.data_entries).to_dict(orient="list"))

    self.timestamps = np.concatenate(
        list(self.dataset.map(lambda x: x["time_stamp"]).batch(100)))

    self.timestamp_buckets = np.linspace(
        self.timestamps.min(),
        self.timestamps.max(),
        num=1000,
    ).tolist()

    self.unique_user_ids = np.unique(
        np.concatenate(
            list(self.dataset.batch(1_000_000).map(lambda x: x["user_id"]))))

    self.layer_sizes = layer_sizes
    self.embedding_dimension = embedding_dimension

    # Compute embeddings for users.
    self.query_model = QueryModel(self.layer_sizes,
                                  self.embedding_dimension,
                                  self.unique_user_ids,
                                  self.timestamps,
                                  self.timestamp_buckets,
                                  use_cross_layer=False,
                                  projection_dim=None)

    self.string_features = self.dataset.map(
      lambda x: {
          "story_id": x["story_id"],
          "story_title": x["story_title"],
          "source_id": x["source_id"],
          "author_id": x["author_id"],
          "most_frequent_keyword": x["most_frequent_keyword"],
          "most_frequent_entity": x["most_frequent_entity"]
        }
      )

    self.int_features = self.dataset.map(
        lambda x: {
            "source_alexa_rank": x["source_alexa_rank"],
            "read_count": x["read_count"],
            "shared_count": x["shared_count"],
            "angry_count": x["angry_count"],
            "cry_count": x["cry_count"],
            "neutral_count": x["neutral_count"],
            "smile_count": x["smile_count"],
            "happy_count": x["happy_count"]
        })

    # Compute embeddings for stories.
    self.candidate_model = CandidateModel(self.layer_sizes,
                                          self.embedding_dimension,
                                          self.string_features,
                                          self.int_features,
                                          use_cross_layer=False,
                                          projection_dim=None)

    # Compute predictions.
    self.rating_model = tf.keras.Sequential([
        # Learn multiple dense layers.
        tf.keras.layers.Dense(256, activation="relu"),
        tf.keras.layers.Dense(128, activation="relu"),
        # Make ranking predictions in the final layer.
        tf.keras.layers.Dense(1)
    ])

    self.ranking_task: tf.keras.layers.Layer = tfrs.tasks.Ranking(
        loss=tf.keras.losses.MeanSquaredError(),
        metrics=[tf.keras.metrics.RootMeanSquaredError()])

    # temp workaround 'TempFactorizedTopK' should be replace with 'tfrs.metrics.FactorizedTopK'
    self.retrieval_task: tf.keras.layers.Layer = tfrs.tasks.Retrieval(
        metrics=TempFactorizedTopK(candidates=self.dataset.batch(
            128).cache().map(self.candidate_model)))

    # The loss weights.
    self.ranking_weight = ranking_weight
    self.retrieval_weight = retrieval_weight

  def call(self, features: Dict[Text, tf.Tensor], training=False) -> tf.Tensor:
    user_embeddings = self.query_model({
        "user_id":
        features["user_id"],
        "time_stamp":
        features["time_stamp"],
    })
    story_embeddings = self.candidate_model({
        "story_id":
        features["story_id"],
        "story_title":
        features["story_title"],
        "source_alexa_rank":
        features["source_alexa_rank"],
        "read_count":
        features["read_count"],
        "shared_count":
        features["shared_count"],
        "angry_count":
        features["angry_count"],
        "cry_count":
        features["cry_count"],
        "neutral_count":
        features["neutral_count"],
        "smile_count":
        features["smile_count"],
        "happy_count":
        features["happy_count"],
        "source_id": features["source_id"],
        "author_id": features["author_id"],
        "most_frequent_keyword": features["most_frequent_keyword"],
        "most_frequent_entity": features["most_frequent_entity"],
    })

    return (
        user_embeddings,
        story_embeddings,
        # We apply the multi-layered rating model to a concatentation of
        # user and movie embeddings.
        self.rating_model(
            tf.concat([user_embeddings, story_embeddings], axis=1)))

  def compute_loss(self,
                   features: Dict[Text, tf.Tensor],
                   training=False) -> tf.Tensor:
    rankings = features.pop("relevancy_rate")

    user_embeddings, story_embeddings, ranking_predictions = self(features)

    ranking_loss = self.ranking_task(
        labels=rankings,
        predictions=ranking_predictions,
    )
    retrieval_loss = self.retrieval_task(user_embeddings, story_embeddings)

    # And combine them using the loss weights.
    return (self.ranking_weight * ranking_loss +
            self.retrieval_weight * retrieval_loss)

  def get_config(self):
    config = {
        "data_entries": self.data_entries,
        "embedding_dimension": self.embedding_dimension,
        "layer_sizes": self.layer_sizes,
        "query_model": self.query_model,
        "candidate_model": self.candidate_model,
        "rating_model": self.rating_model,
        "ranking_task": self.ranking_task,
        "retrieval_task": self.retrieval_task,
        "ranking_weight": self.ranking_weight,
        "retrieval_weight": self.retrieval_weight
    }
    return config

  @classmethod
  def from_config(cls, config):
    conf = {
        "data_entries": config["data_entries"],
        "embedding_dimension": config["embedding_dimension"],
        "layer_sizes": config["layer_sizes"],
        "ranking_weight": config["ranking_weight"],
        "retrieval_weight": config["retrieval_weight"]
    }
    return cls(**conf)


class RankingModel(BaseModel):
  id: bson_id.ObjectIdStr = Field(None, alias="_id")
  ranking_model_id: str
  results: dict


def get_ranking_model():
  mongo_filter = {"ranking_model_id": "1"}
  ranking_models = mongo.get("RankingModel", mongo_filter, limit=1)
  if ranking_models:
    return RankingModel(**ranking_models[0])
  return None


def save_ranking_model(model, eval_dict):
  ranking_model = get_ranking_model()
  if not ranking_model:
    new_ranking_model = {
        "ranking_model_id": "1",
        "results": eval_dict
    }
    model.save_weights(filepath=RANKING_MODEL_WEIGHTS_DIR, save_format="tf")
    model.data_entries.to_parquet(RANKING_MODEL_DATASET_DIR)
    return mongo.add_or_update(new_ranking_model, "RankingModel")
  if eval_dict["root_mean_squared_error"] < ranking_model.results[
      "root_mean_squared_error"]:  # The lower the RMSE metric, the more accurate our model is at predicting ranking
    ranking_model.results = eval_dict
    model.save_weights(filepath=RANKING_MODEL_WEIGHTS_DIR, save_format="tf")
    model.data_entries.to_parquet(RANKING_MODEL_DATASET_DIR)
    return mongo.add_or_update(ranking_model.dict(), "RankingModel")
  return None


def load_ranking_model():
  ranking_model = get_ranking_model()
  if ranking_model:
    data_frame = pd.read_parquet(RANKING_MODEL_DATASET_DIR)
    loaded_model = NewsRankingModel(data_entries=data_frame)
    loaded_model.load_weights(RANKING_MODEL_WEIGHTS_DIR)
    return loaded_model
  return None


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
    if not recent_stories:
      logger.error("Failed to initialize " + language + " index. There was no Data")
      return None
    dataset = tf.data.Dataset.from_tensor_slices(pd.DataFrame.from_dict(recent_stories).to_dict(orient="list"))

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

## End of module
## Temp workaround until https://github.com/tensorflow/recommenders/pull/717 get merged

class TempStreaming(tfrs.layers.factorized_top_k.TopK):
  def __init__(self,
               query_model: Optional[tf.keras.Model] = None,
               k: int = 10,
               handle_incomplete_batches: bool = True,
               num_parallel_calls: int = tf.data.AUTOTUNE,
               sorted_order: bool = True) -> None:

    super().__init__(k=k)
    self.query_model = query_model
    self._candidates = None
    self._handle_incomplete_batches = handle_incomplete_batches
    self._num_parallel_calls = num_parallel_calls
    self._sorted = sorted_order
    self._counter = self.add_weight(name="counter", dtype=tf.int32, trainable=False)
  def index_from_dataset(
      self,
      candidates: tf.data.Dataset
  ) -> "TopK":
    _check_candidates_with_identifiers(candidates)
    self._candidates = candidates
    return self

  def index(  # pytype: disable=signature-mismatch  # overriding-parameter-type-checks
      self,
      candidates: tf.data.Dataset,
      identifiers: Optional[tf.data.Dataset] = None) -> "Streaming":
    raise NotImplementedError(
        "The streaming top k class only accepts datasets. "
        "Please call `index_from_dataset` instead."
    )

  def call(
      self,
      queries: Union[tf.Tensor, Dict[Text, tf.Tensor]],
      k: Optional[int] = None,
  ) -> Tuple[tf.Tensor, tf.Tensor]:
    k = k if k is not None else self._k
    if self._candidates is None:
      raise ValueError("The `index` method must be called first to "
                       "create the retrieval index.")
    if self.query_model is not None:
      queries = self.query_model(queries)
    self._counter.assign(0)

    def top_scores(candidate_index: tf.Tensor,
                   candidate_batch: tf.Tensor) -> Tuple[tf.Tensor, tf.Tensor]:
      scores = self._compute_score(queries, candidate_batch)
      if self._handle_incomplete_batches:
        k_ = tf.math.minimum(k, tf.shape(scores)[1])
      else:
        k_ = k
      scores, indices = tf.math.top_k(scores, k=k_, sorted=self._sorted)
      return scores, tf.gather(candidate_index, indices)

    def top_k(state: Tuple[tf.Tensor, tf.Tensor],
              x: Tuple[tf.Tensor, tf.Tensor]) -> Tuple[tf.Tensor, tf.Tensor]:
      state_scores, state_indices = state
      x_scores, x_indices = x
      joined_scores = tf.concat([state_scores, x_scores], axis=1)
      joined_indices = tf.concat([state_indices, x_indices], axis=1)
      if self._handle_incomplete_batches:
        k_ = tf.math.minimum(k, tf.shape(joined_scores)[1])
      else:
        k_ = k
      scores, indices = tf.math.top_k(joined_scores, k=k_, sorted=self._sorted)
      return scores, tf.gather(joined_indices, indices, batch_dims=1)

    def enumerate_rows(batch: tf.Tensor) -> Tuple[tf.Tensor, tf.Tensor]:
      starting_counter = self._counter.value
      end_counter = self._counter.assign_add(tf.shape(batch)[0])
      return tf.range(starting_counter, end_counter), batch
    if not isinstance(self._candidates.element_spec, tuple):
      candidates = self._candidates.map(enumerate_rows)
      index_dtype = tf.int32
    else:
      candidates = self._candidates
      index_dtype = self._candidates.element_spec[0].dtype
    initial_state = (tf.zeros((tf.shape(queries)[0], 0), dtype=tf.float32),
                     tf.zeros((tf.shape(queries)[0], 0), dtype=index_dtype))
    with _wrap_batch_too_small_error(k):
      results = (
          candidates
          .map(top_scores, num_parallel_calls=self._num_parallel_calls)
          .reduce(initial_state, top_k))
    return results
  def is_exact(self) -> bool:
    return True

class TempFactorizedTopK(tfrs.metrics.factorized_top_k.Factorized):

  def __init__(
      self,
      candidates: Union[tfrs.layers.factorized_top_k.TopK, tf.data.Dataset],
      ks: Sequence[int] = (1, 5, 10, 50, 100),
      name: str = "factorized_top_k",
  ) -> None:
    super().__init__(name=name)
    if isinstance(candidates, tf.data.Dataset):
      candidates = (
          TempStreaming(k=max(ks))
          .index_from_dataset(candidates)
      )
    self._ks = ks
    self._candidates = candidates
    self._top_k_metrics = [
        tf.keras.metrics.Mean(
            name=f"{self.name}/top_{x}_categorical_accuracy"
        ) for x in ks
    ]

  def update_state(
      self,
      query_embeddings: tf.Tensor,
      true_candidate_embeddings: tf.Tensor,
      true_candidate_ids: Optional[tf.Tensor] = None,
      sample_weight: Optional[tf.Tensor] = None,
  ) -> tf.Operation:
    if true_candidate_ids is None and not self._candidates.is_exact():
      raise ValueError(
          f"The candidate generation layer ({self._candidates}) does not return "
          "exact results. To perform evaluation using that layer, you must "
          "supply `true_candidate_ids`, which will be checked against "
          "the candidate ids returned from the candidate generation layer."
      )
    positive_scores = tf.reduce_sum(
        query_embeddings * true_candidate_embeddings, axis=1, keepdims=True)
    top_k_predictions, retrieved_ids = self._candidates(
        query_embeddings, k=max(self._ks))
    update_ops = []
    if true_candidate_ids is not None:
      if len(true_candidate_ids.shape) == 1:
        true_candidate_ids = tf.expand_dims(true_candidate_ids, 1)
      nan_padding = tf.math.is_nan(top_k_predictions)
      top_k_predictions = tf.where(
          nan_padding,
          tf.ones_like(top_k_predictions) * tf.float32.min,
          top_k_predictions
      )
      is_sorted = (
          top_k_predictions[:, :-1] - top_k_predictions[:, 1:]
      )
      tf.debugging.assert_non_negative(
          is_sorted, message="Top-K predictions must be sorted."
      )
      ids_match = tf.cast(
          tf.math.logical_and(
              tf.math.equal(true_candidate_ids, retrieved_ids),
              tf.math.logical_not(nan_padding)
          ),
          tf.float32
      )
      for k, metric in zip(self._ks, self._top_k_metrics):
        match_found = tf.clip_by_value(
            tf.reduce_sum(ids_match[:, :k], axis=1, keepdims=True),
            0.0, 1.0
        )
        metric.update_state(match_found, sample_weight)
        update_ops.append(metric.result())
    else:
      y_pred = tf.concat([positive_scores, top_k_predictions], axis=1)
      for k, metric in zip(self._ks, self._top_k_metrics):
        targets = tf.zeros(tf.shape(positive_scores)[0], dtype=tf.int32)
        top_k_accuracy = tf.math.in_top_k(
            targets=targets,
            predictions=y_pred,
            k=k
        )
        metric.update_state(top_k_accuracy, sample_weight)
        update_ops.append(metric.result())
    return tf.group(update_ops)

def _check_candidates_with_identifiers(candidates: tf.data.Dataset) -> None:
  spec = candidates.element_spec
  if isinstance(spec, tuple):
    if len(spec) != 2:
      raise ValueError(
          "The dataset must yield candidate embeddings or "
          "tuples of (candidate identifiers, candidate embeddings). "
          f"Got {spec} instead."
      )
    identifiers_spec, candidates_spec = spec
    if candidates_spec.shape[0] != identifiers_spec.shape[0]:
      raise ValueError(
          "Candidates and identifiers have to have the same batch dimension. "
          f"Got {candidates_spec.shape[0]} and {identifiers_spec.shape[0]}."
      )

@contextlib.contextmanager
def _wrap_batch_too_small_error(k: int):
  try:
    yield
  except tf.errors.InvalidArgumentError as e:
    error_message = str(e)
    if "input must have at least k columns" in error_message:
      raise ValueError("Tried to retrieve k={k} top items, but the candidate "
                       "dataset batch size is too small. This may be because "
                       "your candidate batch size is too small or the last "
                       "batch of your dataset is too small. "
                       "To resolve this, increase your batch size, set the "
                       "drop_remainder argument to True when batching your "
                       "candidates, or set the handle_incomplete_batches "
                       "argument to True in the constructor. ".format(k=k))
    else:
      raise