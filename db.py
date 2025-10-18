import os
from dotenv import load_dotenv
from pymongo import MongoClient, errors
from bson import ObjectId
from datetime import datetime

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["FollowUpAgent"]
collection = db["tickets"]

# ---------------------------
# Create a new follow-up/task/reminder ticket
# ---------------------------
def create_ticket(type, title, description, action, messages=None):
    """
    Creates a new document and inserts into MongoDB.
    messages: list of messages (optional)
    Returns the inserted document's ID
    """
    if messages is None:
        messages = []

    doc = {
        "type": type,               # "follow-up", "reminder", "task", "other"
        "title": title,              # short summary from Gemini
        "description": description,  # detailed summary
        "action": action,            # suggested action
        "messages": messages,        # list of messages
        "createdAt": datetime.utcnow()
    }

    result = collection.insert_one(doc)
    return result.inserted_id

# ---------------------------
# Append a new message to an existing document
# ---------------------------
def append_message_to_DB(doc_id, new_message):
    """
    Adds a new message to the 'messages' array of an existing document
    doc_id: ObjectId of the document
    """
    result = collection.update_one(
        {"_id": doc_id},
        {"$push": {"messages": new_message}}
    )
    return result.modified_count

# ---------------------------
# Fetch all messages/documents
# ---------------------------
def get_all_documents():
    return list(collection.find())

# ---------------------------
# Fetch only _id and description of all documents
# ---------------------------
def get_documents_id_and_description():
    return list(collection.find({}, {"_id": 1, "description": 1}))