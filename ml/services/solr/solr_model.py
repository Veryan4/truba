from pydantic import BaseModel, Field
from datetime import datetime
import os
import json
import requests
from fastapi.encoders import jsonable_encoder
from services import mongo
from shared import bson_id


class SolrModel(BaseModel):
  id: bson_id.ObjectIdStr = Field(None, alias='_id')
  model_id: str
  linear_model: dict = None
  rank_net_model: dict = None
  model_configuration: dict = None
  score: float = 0.0
  accuracy: float = 0.0
  last_update: datetime = None


def get_solr_model(model_id):
  mongoFilter = {"model_id": model_id}
  solrModels = mongo.get("SolrModels", mongoFilter, limit=1)
  if solrModels:
    solrModel = solrModels[0]
    return SolrModel(**solrModel)
  return None


def load_solr_model_to_store(model_id):
  solrModel = get_solr_model(model_id)
  if not solrModel:
    loadedModel = get_solr_model("defaultmodel")
    if not loadedModel:
      load_default_solr_model()
      loadedModel = get_solr_model("defaultmodel")
    loadedModel.id = None
    loadedModel.model_id = model_id
    linearModel = loadedModel.linear_model
    linearModel.update({"name": model_id})
    add_or_update_to_model_store(linearModel)
    add_or_update_solr_model(loadedModel)
    return loadedModel
  linearModel = solrModel.linear_model
  linearModel.update({"name": model_id})
  add_or_update_to_model_store(linearModel)
  return solrModel


def add_or_update_solr_model(solr_model):
  solr_model.last_update = datetime.utcnow()
  if solr_model.rank_net_model:
    add_or_update_to_model_store(solr_model.rank_net_model)
  return mongo.add_or_update(solr_model.dict(), "SolrModels")


def load_default_solr_model():
  with open('./data/default_model.json') as json_file:
    defaultModel = json.load(json_file)
    add_or_update_to_model_store(defaultModel)
    solrModel = SolrModel(model_id="defaultmodel", linear_model=defaultModel)
    return add_or_update_solr_model(solrModel)
  return None


def reset_model_store(model_ids):
  load_default_solr_model()
  resultsDict = {}
  url = 'http://' + os.getenv("SOLR_HOSTNAME") + ":" + os.getenv(
      "SOLR_PORT") + '/solr/' + os.getenv("ENVIRONMENT") + '/schema/model-store'
  for modelId in model_ids:
    solrModel = load_solr_model_to_store(modelId)
    if solrModel.rank_net_model:
      jsonToPush = jsonable_encoder(solrModel.rank_net_model)
      req = requests.post(url, json=jsonToPush)
      resultsDict.update({modelId: req.text})
    elif solrModel.linear_model:
      jsonToPush = jsonable_encoder(solrModel.linear_model)
      req = requests.post(url, json=jsonToPush)
      resultsDict.update({modelId: req.text})
  return resultsDict


def add_or_update_to_model_store(solr_model):
  jsonToPush = jsonable_encoder(solr_model)
  url = 'http://' + os.getenv("SOLR_HOSTNAME") + ":" + os.getenv(
      "SOLR_PORT") + '/solr/' + os.getenv("ENVIRONMENT") + '/schema/model-store'
  req = requests.post(url, json=jsonToPush)
  return req
