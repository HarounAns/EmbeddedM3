# dbFunc.py
import json

def incrementStat(db, id, board, field):
    post = db.stats.find_one(
        {
            "_id": id
        }
    )

    post["stats"][board][field] = post["stats"][board][field] + 1

    db.stats.update(
        {
            "_id": id
        }, 
        post)