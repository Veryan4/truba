from fastapi import FastAPI, HTTPException
from typing import List
import tensorflow as tf
from services.solr import solr_model
from services import ranking
from shared import tracing

app = FastAPI()
app.add_middleware(tracing.OpentracingMiddleware)

indexes = ranking.get_indexes()
if indexes:
  app.indexEN = indexes["en"]
  app.indexFR = indexes["fr"]
  indexes.clear()


# setup Jaeger Tracer on FastAPI
@app.on_event('startup')
async def startup():
  tracing.init_tracer(app)


@app.post('/model-store/reset')
def reset_solr_models(model_ids: List[str]):
  return solr_model.reset_model_store(model_ids)


@app.get('/model-store/{model_id}')
def add_solr_model(model_id: str):
  model = solr_model.load_solr_model_to_store(model_id)
  return model.dict()


@app.get('/recommendations/{user_id}/{language}')
def get_reccommendations(user_id: str, language: str):
  amount_of_stories = 20
  if language == "en":
    if not app.indexEN:
      raise HTTPException(status_code=404,
                          detail=language + " Index not initialized")
    _, story_ids = app.indexEN(tf.constant([user_id]), k=amount_of_stories)
    story_ids = story_ids.numpy().tolist()[0]
    return tuple(s.decode("utf-8") for s in story_ids)
  if language == "fr":
    if not app.indexFR:
      raise HTTPException(status_code=404, detail="Index not initialized")
    _, story_ids = app.indexFR(tf.constant([user_id]), k=amount_of_stories)
    story_ids = story_ids.numpy().tolist()[0]
    return tuple(s.decode("utf-8") for s in story_ids)
  raise HTTPException(status_code=500, detail=language + " Language not found")
