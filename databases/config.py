import pymongo
from pymongo import AsyncMongoClient
from dotenv import dotenv_values
import os

config = dotenv_values(".env")

client = AsyncMongoClient(
    "mongodb+srv://" + os.environ.get('DB_USER') + ":" + os.environ.get('DB_PASSWORD') + "@cluster0.6bjvmbp.mongodb.net/?appName=Cluster0",
    server_api=pymongo.server_api.ServerApi(version="1", strict=True,deprecation_errors=True)
    )
db = client.get_database("mpen_lyrics")
songs_collection = db.get_collection("songs")