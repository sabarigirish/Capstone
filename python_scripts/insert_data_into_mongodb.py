from random import random
from pymongo import MongoClient
import json
import os


TEXT_FILE_NAME = "twitter_data.json"
ID_FILE_NAME = ""
TEMP_ID_COLLECTION = "tempIDCollection"
TEMP_TEXT_COLLECTION = "tempTextCollection"


def get_data_path():
    current_directory_path = os.getcwd()
    path_array = current_directory_path.strip().split("/")
    path_array[len(path_array)-1] = 'data'
    return "/".join(path_array)


def insert_data(collection_name, id_collection):
    mongo_client = MongoClient('localhost', 3001)
    db = mongo_client.meteor
    new_collection = db[id_collection]
    temp_collection = db[TEMP_ID_COLLECTION]
    id_file_path = get_data_path() + "/" + ID_FILE_NAME
    with open(id_file_path) as input_file:
        for line in input_file:
            document = json.loads(line)
            if document['topic_human'] == 'job' or document['topic_machine'] == 'job':
                new_collection.insert_one(document)
                temp_collection.insert_one(document)

    new_collection = db[collection_name]
    temp_collection = db[collection_name]
    data_file_path = get_data_path() + "/" + TEXT_FILE_NAME
    with open(data_file_path) as input_file:
        for line in input_file:
            document = json.loads(line)
            document['fitnessFuncValue'] = random()
            new_collection.insert_one(document)
            temp_collection.insert_one(document)


def extract_job_realted_tweets(text_collection, id_collection, final_collection):
    mongo_client = MongoClient('localhost', 3001)
    db = mongo_client.meteor

    tweet_id_collection = db[id_collection]
    text_collection = db[text_collection]
    final_coll = db[final_collection]
    tweet_id = []

    for tweet in tweet_id_collection.find():
        tweet_id.append(tweet['tweet_id'])

    # print(tweet_id)

    count = 0
    missing_tweet = []
    for idx in tweet_id:
        data = text_collection.find_one({"id": idx})
        try:
            text = data['text']
            final_coll.insert_one({
            'id': idx,
            'text': text
            })
        except TypeError:
            missing_tweet.append(idx)
            count += 1

    print(missing_tweet)
    print("Total missing tweets: {}".format(count))
    db.drop_collection(id_collection)
    db.drop_collection(text_collection)

if __name__ == '__main__':
    insert_data('newOneYear', 'combinedAnnotation')
    extract_job_realted_tweets(TEMP_TEXT_COLLECTION, TEMP_ID_COLLECTION, 'oneYearData')
