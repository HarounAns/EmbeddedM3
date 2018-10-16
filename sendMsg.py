# sendMsg.py
import sys
import socket
import json
from client import socketSend

host = sys.argv[2]
port = int(sys.argv[4])
message = sys.argv[6]
type_t = sys.argv[8]

if message == 'tag':
    msg = {
            "type": "rover",
            "text": "Chased Rover Tagged",
            "code": 'T',
            "type": 'sensor'
        }
else:
    if not type_t:
        raise ValueError('type is not defined')

    msg = {
            "type": "rover",
            "text": message,
            "length": len(message),
            "code": 'H',
            "type": type_t,
            "pic": 1,
        }

socketSend(msg, host, port)
