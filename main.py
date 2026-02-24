from datetime import datetime
from bson import ObjectId
import json
from fastapi import FastAPI, APIRouter, HTTPException
from pymongo import ReturnDocument
from databases.config import songs_collection
from databases.models import SongModel, SongUpdateModel, SongsCollectionModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket, WebSocketDisconnect


app = FastAPI()
routers = APIRouter()

origins = [
    "http://localhost:5173",
    "https://mpen-songs.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()


@app.websocket("/mpensongsws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive, potentially handling client-sent messages
            data = await websocket.receive_text()
            # Optional: echo or handle client messages
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A client disconnected.")



@routers.get("/api/songs", response_description="Get all songs")
async def songs():
    songs = SongsCollectionModel(songs=await songs_collection.find().to_list())
    return {item.id: item for item in sorted(songs.songs, key=lambda x: x.name)}



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
        
        await manager.broadcast(json.dumps({"status": "new_song", "song": new_song}))
    
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
            await manager.broadcast(json.dumps({"status": "updated_song", "song": updated_song}))
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


app.include_router(routers)