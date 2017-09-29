from random import random
from pymongo import MongoClient
import json
import os


FILE_NAME = "twitter_data.json"


def get_data_path():
    current_directory_path = os.getcwd()
    path_array = current_directory_path.strip().split("/")
    path_array[len(path_array)-1] = 'data'
    return "/".join(path_array)


def insert_data(collection_name):
    mongo_client = MongoClient('localhost', 3001)
    db = mongo_client.meteor
    new_collection = db[collection_name]
    file_path = get_data_path() + "/" + FILE_NAME
    with open(file_path) as input_file:
        for line in input_file:
            document = json.loads(line)
            document['fitnessFuncValue'] = random()
            new_collection.insert_one(document)


if __name__ == '__main__':
    insert_data('oneYearData')
