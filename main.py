from datetime import datetime
from bson import ObjectId
from fastapi import FastAPI, APIRouter, HTTPException, Response, status
from pymongo import ReturnDocument
from databases.config import songs_collection
from databases.models import SongModel, SongUpdateModel, SongsCollectionModel
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
routers = APIRouter()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@routers.get("/api/songs", response_description="Get all songs")
async def songs():
    songs = SongsCollectionModel(songs=await songs_collection.find().to_list())
    return {item.id: item for item in songs.songs}


@routers.get("/api/songs/{song_id}", response_description="Get one song")
async def get_song(song_id : str):
    
    if(song := await songs_collection.find_one({"_id": ObjectId(song_id)})) is not None:
        
        # Do the following to prevent : TypeError("'ObjectId' object is not iterable")
        # It turns ObjectId(_id) into a string 
        song['_id'] = str(song['_id'])
        
        return song
    
    raise HTTPException(status_code=404, detail=f"Song {song_id} not found")
    


@routers.post("/api/songs", response_description="Create a song")
async def create_song(song: SongModel):
    
    try:
        new_song = song.model_dump(by_alias=True, exclude=["id"])
        new_song["created"] = int(datetime.timestamp(datetime.now()))
        result = await songs_collection.insert_one(new_song)
        new_song["_id"] = str(result.inserted_id)
    except Exception as error:
         raise HTTPException(status_code=404, detail=error)
    
    return new_song



@routers.put("/api/songs/{song_id}", response_description="Update a song")
async def put(song_id : str, song: SongUpdateModel):
    
    if(s := await songs_collection.find_one({"_id": ObjectId(song_id)})) is not None:
        s["updated"] = int(datetime.timestamp(datetime.now()))
        updated_song = await songs_collection.find_one_and_update(
            {"_id": ObjectId(song_id)},
            {"$set": s | song.model_dump()},
            return_document=ReturnDocument.AFTER,
        )
        
        updated_song["_id"] = str(updated_song["_id"])
        
        if updated_song is not None:
            return updated_song
        else:
            raise HTTPException(status_code=404, detail=f"Song not found")
        
    raise HTTPException(status_code=400, detail=f"Bad Request")



@routers.delete("/api/songs/{song_id}", response_description="Delete a song",)
async def delete_song(song_id: str):
    
    delete_result = await songs_collection.delete_one({"_id": ObjectId(song_id)})
    if delete_result.deleted_count == 1:
        return song_id
    
    raise HTTPException(status_code=404, detail=f"Song {id} not found")


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
    
app.include_router(routers)