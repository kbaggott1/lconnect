from pydantic import BaseModel

class Location(BaseModel):
    id: int
    longitude: float
    latitude: float
