import sys
from pymongo import MongoClient, errors
import json
import certifi

def load_db(connection_string, db_name):
  client = MongoClient(connection_string, tlsCAFile=certifi.where())
  try:
    client.server_info()
    print('Connected to MongoDB')
  except errors.ServerSelectionTimeoutError as err:
    print(err)
    sys.exit(1)
  
  db = client[db_name]
  client.data
  return db


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
        
        