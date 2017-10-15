from pymongo import MongoClient, ASCENDING, DESCENDING

ACTIVE_TWEET_COLLECTION = "activeTweet"
TWEET_COLLECTION = "oneYearData"

RANDOM_NUMBER = 10


def insert_document(collection_name, final_collection, hit_id):
    mongo_client = MongoClient('localhost', 3001)
    db = mongo_client.meteor
    collection = db[collection_name]
    final = db[final_collection]
    tweet_list = []

    for document in collection.find().sort([("fitnessFuncValue", DESCENDING)]).skip(RANDOM_NUMBER).limit(10):
        tweet_list.append({
            'id': document['id'],
            'text': document['text']
        })

    for document in collection.find().sort([("fitnessFuncValue", DESCENDING)]).skip(
                    (collection.find().count()//2) + RANDOM_NUMBER).limit(10):
        tweet_list.append({
            'id': document['id'],
            'text': document['text']
        })

    for document in collection.find().sort([("fitnessFuncValue", ASCENDING)]).skip(RANDOM_NUMBER).limit(10):
        tweet_list.append({
            'id': document['id'],
            'text': document['text']
        })

    final.insert_one({
        'hitID': hit_id,
        'tweets': tweet_list
    })


def create_document(hit_id):
    insert_document(TWEET_COLLECTION, ACTIVE_TWEET_COLLECTION, hit_id)