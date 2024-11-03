from pymongo import MongoClient
import datetime

# MongoDB connection setup
client = MongoClient("mongodb+srv://bmowinski2:4K4cR171KB6uLPVT@team33data.5p0rb.mongodb.net/?retryWrites=true&w=majority&appName=team33data")
db = client.language_learning_app
users_collection = db.users
sentences_collection = db.sentences
attempted_sentences_collection = db.attempted_sentences

# Dummy data
dummy_users = [
    {"name": "Alices Smith", "email": "alice@example.com"},
    {"name": "Bobby Johnson", "email": "bob@example.com"}
]

dummy_sentences = [
    {"text": "Peter Piper picked a peck of pickled peppers. A peck of pickled peppers Peter Piper picked. If Peter Piper picked a peck of pickled peppers,Where’s the peck of pickled peppers Peter Piper picked?"},
    {"text": "She sells seashells by the seashore."},
    {"text": "She sells seashells by the seashore."},
    {"text": "She sells seashells by the seashore."},
    {"text": "How can a clam cram in a clean cream can?"}
]

dummy_attempted_sentences = [
    {
        "user_id": None,  # will be set later
        "sentence_id": None,  # will be set later
        "accuracy_score": 85.0,
        "fluency_score": 90.0,
        "completeness_score": 95.0,
        "overall_score": 90.0,
        "timestamp": datetime.datetime.utcnow()
    }
]

def initialize_dummy_data():
    # Check and add users
    if users_collection.count_documents({}) == 0:
        print("Adding dummy users...")
        user_ids = [users_collection.insert_one(user).inserted_id for user in dummy_users]
        print("Dummy users added:", user_ids)
    else:
        print("Users collection already has data.")

    # Check and add sentences
    if sentences_collection.count_documents({}) == 0:
        print("Adding dummy sentences...")
        sentence_ids = [sentences_collection.insert_one(sentence).inserted_id for sentence in dummy_sentences]
        print("Dummy sentences added:", sentence_ids)
    else:
        print("Sentences collection already has data.")

    # Check and add attempted sentences
    if attempted_sentences_collection.count_documents({}) == 0:
        print("Adding dummy attempted sentences...")
        for attempt in dummy_attempted_sentences:
            attempt["user_id"] = user_ids[0]  # Associate with the first dummy user
            attempt["sentence_id"] = sentence_ids[0]  # Associate with the first dummy sentence
            attempted_sentences_collection.insert_one(attempt)
        print("Dummy attempted sentences added.")
    else:
        print("Attempted sentences collection already has data.")

# Run the initialization
initialize_dummy_data()
