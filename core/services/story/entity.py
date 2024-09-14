from typing import Tuple

from services import mongo
import project_types

DB_COLLECTION_NAME = "Entity"


def add_new_entities(entities: Tuple[project_types.Entity, ...]):
  """Stores new entities to the Mongo database.

    Args:
        entities: The entities to store.

    Returns:
        If there are new entities to add it returns the Mongo result,
        otherwise it returns None.

    """

  entity_links = set()
  unique_entities = tuple(
      entity_links.add(ent.links) or ent for ent in entities
      if ent.links not in entity_links)
  # search to see whether the entity already exists in db
  new_entity_links = tuple(entity.links for entity in unique_entities)
  mongo_filter = {"links": {"$in": new_entity_links}}
  current_entities = mongo.get(DB_COLLECTION_NAME, mongo_filter)
  current_entity_links = tuple(entity["links"] for entity in current_entities)
  entities_to_push = tuple(entity.dict() for entity in unique_entities
                           if entity.links not in current_entity_links)
  if entities_to_push:
    return mongo.add_or_update(entities_to_push, DB_COLLECTION_NAME)
  return None


def get_by_links(entity_links: Tuple[str, ...]) -> Tuple[project_types.Entity]:
  """Retrieves a list of Entities from the database given their ids.

    Args:
        entity_ids: The list of entity ids.

    Returns:
        The Authors if found, otherwise None.

    """

  mongo_filter = {"links": {"$in": list(entity_links)}}
  entities = mongo.get(DB_COLLECTION_NAME,
                       mongo_filter,
                       limit=len(entity_links))
  return tuple(project_types.Entity(**entity) for entity in entities)
