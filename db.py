from pymongo import MongoClient

MONGODB_URI = 'mongodb+srv://JuanCote:tfkn7C64u55PFtl4@cluster0.lecracw.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(MONGODB_URI)
db = client.Sanyok

cards = db.cards
stats = db.stats
users = db.users
websockets = db.websockets
