from pymongo import MongoClient

client = MongoClient("mongodb://root:password@localhost:27017/FollowUpAgent?authSource=admin")
db = client["FollowUpAgent"]

# Example: check connection and print databases
print(db.list_collection_names())
