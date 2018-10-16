# printStats
# pretty prints the stats JSON in the MongoDB

import pprint
from pymongo import MongoClient

pp = pprint.PrettyPrinter(indent=4)
client = MongoClient('mongodb://localhost:27017/')
db = client.roverMessages

post = db.stats.find_one(
        {
            "stats": { '$exists' : True }
        }
    )

pp.pprint(post)