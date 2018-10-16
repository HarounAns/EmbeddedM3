# sendToDb.py
from pymongo import MongoClient

def sendToDb(client, msg):
    db = client.roverMessages
    db.roverMessages.insert(msg)

msg = {"roverMsg": "tagged", "code": 'T'}
client = MongoClient('mongodb://localhost:27017/')
sendToDb(client, msg)
print('Message Inserted')
