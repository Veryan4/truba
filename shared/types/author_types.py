from pydantic import BaseModel, Field
from typing import List
from uuid import UUID, uuid4
from shared import bson_id
from shared.types import source_types


class Author(BaseModel):
  id: bson_id.ObjectIdStr = Field(None, alias='_id')
  author_id: UUID = Field(default_factory=uuid4)
  name: str = None
  affiliation: List[source_types.Source] = None
  reputation: float = 0.0


def mock_author() -> Author:
  return Author(id="0912309120923",
                author_id=UUID("3d925894-7c07-4d70-be56-09f8e1f1071c"),
                name="Tom Lundy",
                affiliation=[source_types.mock_source()],
                reputation=0.0)
