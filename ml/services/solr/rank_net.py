import requests
import os
import json
import numpy as np
from fastapi.encoders import jsonable_encoder
from tensorflow.keras.layers import Activation, Add, Dense, Input, Lambda
from tensorflow.keras.models import Model, model_from_json
from tensorflow.keras.metrics import categorical_accuracy
from typing import List
from pydantic import BaseModel, Field

from services.solr import solr_model
from services import mongo
from shared.types import search_types
from shared import bson_id

current_module = 'rank_net'
max_score = 1.0
min_accuracy = 0.0


class TrainingSet(BaseModel):
  id: bson_id.ObjectIdStr = Field(None, alias='_id')
  model_id: str
  Features: List[List[float]]
  Targets: List[int]
  Ranks: List[int]


def get_stories_from_solr(modelId):
  numberOfDays = 10
  storiesPerDay = 24

  currentStories = []
  documents = []

  for day in range(0, numberOfDays):

    startDate: str = day
    endDate: str = day - 1

    ltrParams = search_types.LtrParams(
        model_name="defaultmodel",
        request_handler="query",
        params=[{
            "efi.querytext": "*"
        }],
        fields=["id", "score", "StoryId", "[features]"])

    searchQuery = search_types.SearchQuery(terms="*",
                                           user_id=modelId,
                                           count=storiesPerDay,
                                           start_date=startDate,
                                           end_date=endDate,
                                           learn_to_rank_params=ltrParams,
                                           Grouped="",
                                           Sort="")

    response = requests.get("http://" + os.getenv("CORE_HOSTNAME") + ":" +
                            os.getenv("CORE_PORT") + "/solr/features",
                            json=jsonable_encoder(searchQuery))
    if response:
      docs = response.json()
      for doc in docs:
        storyId = doc["StoryId"][0]
        if storyId not in currentStories:
          currentStories.append(currentStories)
          documents.append(doc)
  return documents


def rank_net(modelId):
  solrDocuments = get_stories_from_solr(modelId)
  RERANK = len(solrDocuments)

  # Extract the features.
  results_features = []
  results_targets = []
  results_ranks = []
  add_data = False

  dataSet = []  ## Need to repurpose RankingData
  # Should experiment with different minimum relevancy_rate values.
  relevantStoryIds = [
      d["StoryId"] for d in dataSet["Data"] if d["relevancy_rate"] > 0
  ]

  for (rank, document) in enumerate(solrDocuments):

    features = document["[features]"].split(",")
    feature_array = []
    for feature in features:
      feature_array.append(feature.split("=")[1])

    results_features.append(feature_array)

    doc_id = document["StoryId"][0]
    # Check if document is relevant to query.
    if doc_id in relevantStoryIds:
      results_ranks.append(rank + 1)
      results_targets.append(1)
      add_data = True
    else:
      results_targets.append(0)

  if add_data:
    trainingSet = TrainingSet(model_id=modelId,
                              Features=results_features,
                              Targets=results_targets,
                              Ranks=results_ranks)
    save_training_set(trainingSet)
  else:
    return None

  ranks = []
  Xs = []

  trainingSets = get_training_sets(modelId)
  for trainingSet in trainingSets:
    X = np.array(trainingSet.Features)
    if X.shape[0] != RERANK:
      continue

    npRank = np.array(trainingSet.Ranks)
    rank = npRank[0]
    ranks.append(rank)
    pos_example = X[rank - 1]
    for (i, neg_example) in enumerate(X):
      if i == rank - 1:
        continue
      Xs.append(np.concatenate((pos_example, neg_example)))

  X = np.stack(Xs)
  dim = int(X.shape[1] / 2)

  train_per = 0.8
  train_cutoff = int(train_per * len(ranks)) * (RERANK - 1)

  train_X = X[:train_cutoff]
  test_X = X[train_cutoff:]

  Y = np.ones((train_X.shape[0], 1))
  train_Y = Y[:train_cutoff]
  test_Y = Y[train_cutoff:]

  INPUT_DIM = dim
  h_1_dim = 64
  h_2_dim = h_1_dim // 2
  h_3_dim = h_2_dim // 2

  # Model.
  h_1 = Dense(h_1_dim, activation="relu")
  h_2 = Dense(h_2_dim, activation="relu")
  h_3 = Dense(h_3_dim, activation="relu")
  s = Dense(1)

  # Relevant document score.
  rel_doc = Input(shape=(INPUT_DIM, ), dtype="float32")
  h_1_rel = h_1(rel_doc)
  h_2_rel = h_2(h_1_rel)
  h_3_rel = h_3(h_2_rel)
  rel_score = s(h_3_rel)

  # Irrelevant document score.
  irr_doc = Input(shape=(INPUT_DIM, ), dtype="float32")
  h_1_irr = h_1(irr_doc)
  h_2_irr = h_2(h_1_irr)
  h_3_irr = h_3(h_2_irr)
  irr_score = s(h_3_irr)

  # Subtract scores.
  negated_irr_score = Lambda(lambda x: -1 * x, output_shape=(1, ))(irr_score)
  diff = Add()([rel_score, negated_irr_score])

  # Pass difference through sigmoid function.
  prob = Activation("sigmoid")(diff)

  # Build model.
  model = Model(inputs=[rel_doc, irr_doc], outputs=prob)
  model.compile(optimizer="adagrad",
                loss="binary_crossentropy",
                metrics=[categorical_accuracy])

  NUM_EPOCHS = 30
  BATCH_SIZE = 32
  model.fit([train_X[:, :dim], train_X[:, dim:]],
            Y,
            epochs=NUM_EPOCHS,
            batch_size=BATCH_SIZE,
            validation_split=0.05,
            verbose=2)

  score, acc = model.evaluate([test_X[:, :dim], test_X[:, dim:]],
                              batch_size=BATCH_SIZE)

  oldrank_net_model = solr_model.get_solr_model(modelId)
  if oldrank_net_model:
    max_score = oldrank_net_model.score
    min_accuracy = oldrank_net_model.accuracy

  if score < max_score and acc > min_accuracy:
    json_config = model.to_json()
    dict_config = json.load(json_config)

    weights = model.get_weights()

    solr_model = {
        "store":
        "efi_feature_store",
        "name":
        modelId,
        "class":
        "org.apache.solr.ltr.model.NeuralNetworkModel",
        "features": [{
            "name": "documentRecency",
            "norm": {
                "class": "org.apache.solr.ltr.norm.IdentityNormalizer"
            }
        }, {
            "name": "tfidf_sim_title",
            "norm": {
                "class": "org.apache.solr.ltr.norm.IdentityNormalizer"
            }
        }, {
            "name": "bm25_sim_title",
            "norm": {
                "class": "org.apache.solr.ltr.norm.IdentityNormalizer"
            }
        }, {
            "name": "tfidf_sim_body",
            "norm": {
                "class": "org.apache.solr.ltr.norm.IdentityNormalizer"
            }
        }, {
            "name": "bm25_sim_body",
            "norm": {
                "class": "org.apache.solr.ltr.norm.IdentityNormalizer"
            }
        }, {
            "name": "tfidf_sim_keywords",
            "norm": {
                "class": "org.apache.solr.ltr.norm.IdentityNormalizer"
            }
        }, {
            "name": "bm25_sim_keywords",
            "norm": {
                "class": "org.apache.solr.ltr.norm.IdentityNormalizer"
            }
        }, {
            "name": "tfidf_sim_entities",
            "norm": {
                "class": "org.apache.solr.ltr.norm.IdentityNormalizer"
            }
        }, {
            "name": "bm25_sim_entities",
            "norm": {
                "class": "org.apache.solr.ltr.norm.IdentityNormalizer"
            }
        }],
        "params": {
            "layers": [{
                "matrix": weights[0].T.tolist(),
                "bias": weights[1].tolist(),
                "activation": "relu"
            }, {
                "matrix": weights[2].T.tolist(),
                "bias": weights[3].tolist(),
                "activation": "relu"
            }, {
                "matrix": weights[4].T.tolist(),
                "bias": weights[5].tolist(),
                "activation": "relu"
            }, {
                "matrix": weights[6].T.tolist(),
                "bias": weights[7].tolist(),
                "activation": "identity"
            }]
        }
    }

    if oldrank_net_model:
      oldrank_net_model.model_config = dict_config
      oldrank_net_model.RankNetConfig = solr_model
      oldrank_net_model.score = score
      oldrank_net_model.accuracy = acc
      solr_model.add_or_update_solr_model(oldrank_net_model)
      return oldrank_net_model
    else:
      rankNetModel = solr_model.SolrModel(model_id=modelId,
                                          model_config=dict_config,
                                          RankNetConfig=solr_model,
                                          score=score,
                                          accuracy=acc)
      solr_model.add_or_update_solr_model(rankNetModel)
      return rankNetModel
  return None


def save_training_set(trainingSet):
  result = mongo.add_or_update(trainingSet.dict(), "TrainingSet")
  return result


def get_training_sets(modelId):
  mongoFilter = {"model_id": modelId}
  results = mongo.get("TrainingSet", mongoFilter)
  trainingSets = [TrainingSet(**r) for r in results]
  return trainingSets
