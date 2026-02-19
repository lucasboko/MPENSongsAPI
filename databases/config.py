import pymongo
from pymongo import AsyncMongoClient
from dotenv import dotenv_values

config = dotenv_values(".env")

client = AsyncMongoClient(
    "mongodb+srv://lucasboko_db_user:a1IOfOm5FVvEpaAQ@cluster0.6bjvmbp.mongodb.net/?appName=Cluster0",
    server_api=pymongo.server_api.ServerApi(version="1", strict=True,deprecation_errors=True)
    )
db = client.get_database("mpen_lyrics")
songs_collection = db.get_collection("songs")