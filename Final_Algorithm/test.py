""" An example of how to insert a document """
import sys

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

client = MongoClient()
db = client.test

result = db.URLCollection.insert_one(
    {
        "address": "URL"
    }
)