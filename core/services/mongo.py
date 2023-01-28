from pymongo import MongoClient, InsertOne, UpdateOne, ASCENDING, DESCENDING
import os
from typing import List, Union


def db_connection():
  """Retrieves the connection to the Mongo database.

    Returns:
        The mongo DB connection

    """

  db_name = os.getenv("ENVIRONMENT")
  mongo_uri = "mongodb://" + os.getenv("MONGO_USERNAME") + ":" + os.getenv(
      "MONGO_PASSWORD") + "@" + os.getenv(
          "CORE_DB_HOSTNAME") + ".default.svc.cluster.local:" + os.getenv(
              "CORE_DB_PORT") + "/" + db_name + "?authSource=admin"
  my_client = MongoClient(mongo_uri, uuidRepresentation="standard")
  return my_client[db_name]


def get(collection_name: str,
        mongo_filter: dict,
        limit: int = None,
        sort: str = None,
        reverse: bool = False,
        distinct: str = "") -> List[dict]:
  """A generic call to the Mongo DB in order to retrieve documents.

    Args:
        collection_name: The name of the collection in the database to be
          retrieved.
        mongo_filter: A dictionary of values which can be used to filter the
          returned results.
        limit: The amount of documents to be retrieved.
        sort: If provided, orders the documents based on the sort key.
        reverse: If the sort argument is provided, it will turn the order of
          values to Descending.
        distinct: If provided, only the unique values of the distinct key are
          returned.

    Returns:
        A list of documents formated as python dictionaries.

    """

  my_db = db_connection()
  my_col = my_db.get_collection(collection_name)
  results = my_col.find(mongo_filter)
  if distinct:
    results = results.distinct(distinct)
    if limit:
      results = results[:limit]
    return results
  if sort:
    if reverse:
      results = results.sort(sort, DESCENDING)
    else:
      results = results.sort(sort, ASCENDING)
  if limit:
    results = results.limit(limit)
  # Cursor to List
  result_list = [result for result in results]
  return result_list


def get_grouped(collection_name: str,
                mongo_filter: dict,
                group_by: str,
                limit: int = None,
                sort: str = None,
                reverse: bool = False) -> List[dict]:
  """Retrieved documents from Mongo database grouped by a specific value.

    Args:
        collection_name: The name of the collection in the database to be
          retrieved.
        mongo_filter: A dictionary of values which can be used to filter the
          returned results.
        group_by: The key that is used to group the documents returned by mongo.
        limit: The amount of documents to be retrieved.
        sort: If provided, orders the documents based on the sort key.
        reverse: If the sort argument is provided, it will turn the order of
          values to Descending.

    Returns:
        A list of documents formated as python dictionaries.

    """

  my_db = db_connection()
  my_col = my_db.get_collection(collection_name)
  results = my_col.find(mongo_filter)
  aggregate = []
  aggregate.append({"$match": mongo_filter})
  group = {"$group": {"_id": ("$" + group_by), "items": {"$push": "$$ROOT"}}}
  aggregate.append(group)
  if sort:
    if reverse:
      aggregate.append({"$sort": {sort: -1}})
    else:
      aggregate.append({"$sort": {sort: 1}})
  if limit:
    aggregate.append({"$limit": limit})
  results = my_col.aggregate(aggregate)
  return [result["items"][0] for result in results if result["items"]]


def add_or_update(documents: Union[List[dict], dict], collection_name: str):
  """A generic call to the Mongo DB to either add or update a document.
    If a BSON _id or id is found on a dictionary it already exists in the
    database and will be updated. Otherwise the dictionary is created in the database.

    Args:
        documents: The dictionaries top be created or updated in Mongo.
        collection_name: The name of the collection in the database to be updated.

    Returns:
        The mongo bulk api result.

    """

  my_db = db_connection()
  my_col = my_db.get_collection(collection_name)
  if my_col is None:
    return "Collection Name is Incorrect!"
  if not documents:
    return "documents list is empty"
  if type(documents) != list and type(documents) != tuple:
    documents = [documents]
  operations = []
  for document in documents:
    if "_id" in document and document["_id"]:
      operations.append(
          UpdateOne({"_id": document["_id"]}, {"$set": document}, upsert=True))
    elif "id" in document and document["id"]:
      operations.append(
          UpdateOne({"_id": document["id"]}, {"$set": document}, upsert=True))
    else:
      operations.append(InsertOne(document))
  response = my_col.bulk_write(operations)
  return response.bulk_api_result


def remove(collection_name: str, mongo_filter: dict) -> int:
  """Remove documents from the mongo database.

    Args:
        collection_name: The name of the collection in the database where
          documents are to be deleted.
        mongo_filter: A dictionary of values which can be used to mark which
          documents to be deleted.

    Returns:
        The int number of deleted documents

    """

  my_db = db_connection()
  my_col = my_db.get_collection(collection_name)
  result = my_col.delete_many(mongo_filter)
  return result.deleted_count


def get_field_with_longest_list(collection_name: str, mongo_filter: dict,
                                field: str) -> dict:
  """Retrieve the document from Mongo database with the highest value
  for a given key.

    Args:
        collection_name: The name of the collection in the database to be
          retrieved.
        mongo_filter: A dictionary of values which can be used to filter the
          returned results.
        field: The key of the document which will be use to rank the documents.

    Returns:
        The one desired document formated as a python dictionary.

    """

  my_db = db_connection()
  my_col = my_db.get_collection(collection_name)
  aggregate = [{
      '$match': mongo_filter
  }, {
      '$unwind': '$' + field
  }, {
      '$group': {
          '_id': '$_id',
          'len': {
              '$sum': 1
          }
      }
  }, {
      '$sort': {
          'len': -1
      }
  }, {
      '$limit': 1
  }]
  cursor_results = my_col.aggregate(aggregate)
  results = [result for result in cursor_results]
  filter2 = {'_id': results[0]['_id']}
  return get(collection_name, filter2, 1)[0]
