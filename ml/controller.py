from fastapi import FastAPI, HTTPException
import tensorflow as tf
from dotenv import load_dotenv
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from services import ranking

load_dotenv()

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)

indexes = {}

@app.on_event("startup")
def init_data():
  ranking_indexes = ranking.get_indexes()
  if ranking_indexes:
    indexes.update({"en": ranking_indexes["en"]})
    indexes.update({"fr": ranking_indexes["fr"]})
    ranking_indexes.clear()
  return indexes

@app.get("/recommendations/{user_id}/{language}")
def get_reccommendations(user_id: str, language: str):
  amount_of_stories = 20
  if language == "en":
    if "en" not in indexes:
      raise HTTPException(status_code=404,
                          detail=language + " Index not initialized")
    _, story_ids = indexes["en"](tf.constant([user_id]), k=amount_of_stories)
    story_ids = story_ids.numpy().tolist()[0]
    return tuple(s.decode("utf-8") for s in story_ids)
  if language == "fr":
    if "fr" not in indexes:
      raise HTTPException(status_code=404, detail="Index not initialized")
    _, story_ids = indexes["fr"](tf.constant([user_id]), k=amount_of_stories)
    story_ids = story_ids.numpy().tolist()[0]
    return tuple(s.decode("utf-8") for s in story_ids)
  raise HTTPException(status_code=500, detail=language + " Language not found")
