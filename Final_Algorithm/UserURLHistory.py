import re
import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def getURLsFromPage(pageContents):
	return re.findall(r'(https?://[^\s]+)', pageContents)

def  insertURLsInDB(urlList):
	if len(urlList) == 0:
		return
	for oneURL in urlList:
		client = MongoClient()
		db = client.test

		result = db.URLCollection.insert_one(
		    {
		        "address": oneURL
		    }
		)
def insertURLIntoDB(url):
	client = MongoClient()
	db = client.test

	result = db.URLCollection.insert_one(
	    {
	        "address": url
	    }
	)
def findAllURLs():
	client = MongoClient()
	db = client.test

	cursor = db.URLCollection.find()
	urlList = []
	for document in cursor:
		urlList.append(document["address"])
	return urlList
def findURL(url):
	client = MongoClient()
	db = client.test
	cursor = db.URLCollection.find({"address":url})

	for document in cursor:
		return True
	return False

def greaterThenValue(n):
	client = MongoClient()
	db = client.test
	cursor = list(db.URLCollection.aggregate([
	{"$group" : {"_id" : "$address", "count":  { "$sum" : 1}}
	}]))
	urlList =[]
	for document in cursor:
		if document["count"]>=n:
			urlList.append(document["_id"])
	return urlList

def findTopN(n):
	client = MongoClient()
	db = client.test
	cursor = list(db.URLCollection.aggregate([
	{"$group" : {"_id" : "$address", "count":  { "$sum" : 1}}
	},
	{"$limit": n}]))
	urlList = []
	for document in cursor:
		urlList.append(document["_id"])
	return urlList
print findAllURLs()