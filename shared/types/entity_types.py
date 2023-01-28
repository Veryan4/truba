from pydantic import BaseModel, Field
from shared import bson_id


class Entity(BaseModel):
  id: bson_id.ObjectIdStr = Field(None, alias='_id')
  text: str
  type: str
  links: str


class EntityInStory(BaseModel):
  entity: Entity
  frequency: int

class EntityInStoryDB(BaseModel):
  links: str
  frequency: int


def mock_entity() -> Entity:
  return Entity(id="9876456345", text="Apple", type="ORG", links="AppleORG")


def mock_entity_in_story() -> EntityInStory:
  t = EntityInStory(entity=mock_entity(), frequency=0)
  return t
