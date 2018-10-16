# server.py

import sys
import socket
import json
from cache import values 
import _thread as thread
import time
import dbFunc
from sendToDb import sendToDb
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client.roverMessages

def on_new_client(clientsocket,addr):
    while True:
        data = clientsocket.recv(1024) 
        ACK = False

        if not data:
            break

        #do some checks and if data == someWeirdSignal: break:
        print (addr, ' >> ', data)

        # parse data and return response
        try:
            data = json.loads(data.decode())
        except:
            try:
                data = data.decode()
                print('Data is not JSON')
            except:
                print('Data is a non decodable bytestream')
                print(data)
                print(type(data))
                # construct Dict from bytestream
                

        if isinstance(data, str):
            if data == '*HELLO*':
                ACK = True
                # response = 'Connected to Server!'
            else:
                response = 'Please send JSON'
        elif type(data) is bytes and len(data) > 3:
                response = [0 for i in range(10)]

                # check if acknowledgement
                if data[3] == 3:
                    ACK = True
                    dbFunc.incrementStat(db, stats_id, "pic32", "repliesReceived")
                else:
                    # if not an acknowledgment
                    for i in range(0, len(data)):
                        if i == 3:
                            response[i] = 3
                        else:
                            response[i] = data[i]
                    
                    # check response and increment requests
                    if data[0] != 180 or data[9] != 199 or data[3] == 4:
                        print("Invalid Request")
                        dbFunc.incrementStat(db, stats_id, "server", "missedRequests")
                    else:
                        dbFunc.incrementStat(db, stats_id, "server", "requestsReceived")

                    # increment Requests Sent for specific pic board
                    if data[1] == 1:
                        dbFunc.incrementStat(db, stats_id, "pic1", "requestsSent")
                    elif data[1] == 2:
                        dbFunc.incrementStat(db, stats_id, "pic2", "requestsSent")
                    elif data[1] == 3:
                        dbFunc.incrementStat(db, stats_id, "pic3", "requestsSent")

                    # turn into byte stream
                    response = bytes(response)
        else:
            # if data sent is 'waiting for rover signal'
            if data["code"] == 'W':
                # pause the thread until it receives a rover type message
                while 1:
                    if db.roverMessages.find_one():
                        print(db.roverMessages.find_one())
                        db.roverMessages.remove({})
                        response = 'Tagged'
                        break

            # signal from Hardware
            elif data["code"] == 'H':
                if len(data["text"]) != data["length"]:
                    print("Incrementing number of missed requests")
                    dbFunc.incrementStat(db, stats_id, "server", "missedRequests")

                # If it is okay
                else:
                    print("Message Received:")
                    print(data["text"])
                    print('Incrementing requests received')
                    dbFunc.incrementStat(db, stats_id, "server", "requestsReceived")

                # if tagged message update the db so that GUI updates
                if data["text"] == 'tag':
                    msg = {"roverMsg": "tagged", "code": 'T'}
                    db.roverMessages.insert(msg)

                # increment Requests Sent for specific pic board
                if data["pic"] == 1:
                    dbFunc.incrementStat(db, stats_id, "pic1", "requestsSent")
                elif data["pic"] == 2:
                    dbFunc.incrementStat(db, stats_id, "pic2", "requestsSent")
                elif data["pic"] == 3:
                    dbFunc.incrementStat(db, stats_id, "pic3", "requestsSent")

                # check to see if updated
                print('Updated DB')
                print(db.stats.find_one(stats_id))
                
                # Send reply
                response = 'Got Message from Hardware: ' + data["text"]

            elif data["code"] == 'S':
                response = 'Starting Rovers'

            elif data["code"] == 'R':
                response = 'Resetting Rovers'

            elif data["code"] == 'P':
                response = 'Pausing Rovers'

            elif data["code"] == 'M':
                response = data["text"]

            elif data["code"] == 'T':
                response = data["text"]
            
            else:
                response = 'Unrecognized Message'
        
        if clientsocket and not ACK:
            if type(response) is not bytes:
                response = response.encode()
            else:
                print('Response for bytes')
                print(response)
            
            clientsocket.send(response)

            #increment repliesSent
            dbFunc.incrementStat(db, stats_id, "server", "repliesSent") 

    clientsocket.close()


host = ''
port = int(sys.argv[2])
size = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to the host (this server) and to a predefined port from command line
s.bind((host, int(port)))
print('binding to port: ' + str(port) + ' and host: ' + str(host))

# initialize database with json collections
db.stats.remove({})
db.roverMessages.remove({})
post = {
    "stats": {
        "pic1": {
            "requestsSent": 0,
            "repliesReceived": 0,
            "missedReplies": 0
        },
        "pic2": {
            "requestsSent": 0,
            "repliesReceived": 0,
            "missedReplies": 0
        },
        "pic3": {
            "requestsSent": 0,
            "repliesReceived": 0,
            "missedReplies": 0
        },
        "server": {
            "requestsReceived": 0,
            "missedRequests": 0,
            "repliesSent": 0,
            "incorrectReplies": 0   
        }
    }   
}
stats_id = db.stats.insert_one(post).inserted_id

# wait for incoming connections from clients
s.listen(size)
while 1:
    c, addr = s.accept()     # Establish connection with client.
    thread.start_new_thread(on_new_client,(c,addr))
s.close()
