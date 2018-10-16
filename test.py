# test.py
import pprint
from pymongo import MongoClient
from client import socketSend

client = MongoClient('mongodb://localhost:27017/')
db = client.roverMessages
host = '172.29.115.227'
port = 6000
pp = pprint.PrettyPrinter(indent=4)

# test that the database gets updated
def test_message_received():
    originalPost = db.stats.find_one(
        {
            "stats": { '$exists' : True }
        }
    )

    # Valid Message where length = length of text
    msg = {
        "type": "rover",
        "text": "Chased Rover Tagged",
        "length": len("Chased Rover Tagged"),
        "code": 'H',
        "type": 'motors',
        "pic": 1
    }

    socketSend(msg, host, port)

    # check to see if stats are updated
    newPost = db.stats.find_one(
        {
            "stats": { '$exists' : True }
        }
    )

    # Output before and after
    print("\n---------------------------------------------------\n")
    print("Original Post")
    pp.pprint(originalPost)
    print("Updated Post")
    pp.pprint(newPost)
    print("\n---------------------------------------------------\n")

    
    assert type(newPost) is dict
    assert newPost != originalPost
    assert newPost["stats"]["pic1"]["requestsSent"] == originalPost["stats"]["pic1"]["requestsSent"] + 1
    assert newPost["stats"]["server"]["requestsReceived"] == originalPost["stats"]["server"]["requestsReceived"] + 1

def test_message_missed():
    originalPost = db.stats.find_one(
        {
            "stats": { '$exists' : True }
        }
    )

    # Invalid Message where length is incorrect (len - 1)
    msg = {
        "type": "rover",
        "text": "Chased Rover Tagged",
        "length": len("Chased Rover Tagged") - 1,
        "code": 'H',
        "type": 'motors',
        "pic": 1
    }

    socketSend(msg, host, port)

    # check to see if stats are updated
    newPost = db.stats.find_one(
        {
            "stats": { '$exists' : True }
        }
    )

    # Output before and after
    print("\n---------------------------------------------------\n")
    print("Original Post")
    pp.pprint(originalPost)
    print("Updated Post")
    pp.pprint(newPost)
    print("\n---------------------------------------------------\n")
    
    assert type(newPost) is dict
    assert newPost != originalPost
    assert newPost["stats"]["pic1"]["requestsSent"] == originalPost["stats"]["pic1"]["requestsSent"] + 1
    assert newPost["stats"]["server"]["missedRequests"] == originalPost["stats"]["server"]["missedRequests"] + 1