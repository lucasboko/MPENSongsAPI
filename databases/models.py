from typing import Annotated, List, Optional
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from datetime import datetime

PyObjectId = Annotated[str, BeforeValidator(str)]


class NewSongModel(BaseModel):
    name: str
    lyrics: str
    artist: str
    album: str
    created: int
    updated: int = int(datetime.timestamp(datetime.now()))
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Yahweh", 
                "lyrics": "You are Yahweh", 
                "artist": "Steve Crown", 
                "album": "Faith Is Rising", 
                # "created": "2016-01-01", 
                # "updated": "2016-01-01"
            }
        },
    )
    
class SongUpdateModel(BaseModel):
    name: str
    lyrics: str
    artist: str
    album: str
    
    
class SongModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    lyrics: str
    artist: str
    album: str
    created: int = int(datetime.timestamp(datetime.now()))
    updated: int = int(datetime.timestamp(datetime.now()))
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Yahweh", 
                "lyrics": "You are Yahweh", 
                "artist": "Steve Crown", 
                "album": "Faith Is Rising", 
                # "created": "2016-01-01", 
                # "updated": "2016-01-01"
            }
        },
    )

class SongsCollectionModel(BaseModel):
    songs: List[SongModel]

 