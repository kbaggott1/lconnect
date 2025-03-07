from location import Location
from fastapi import FastAPI, HTTPException, status as STATUS_CODE
from db import Database

# app = FastAPI(docs_url=None, redoc_url=None)
app = FastAPI() # Remove this when prod
db = Database()

@app.put("/loc/{id}")
async def update_location(id: int, location: Location):
    if id != location.id:
        raise HTTPException(STATUS_CODE.HTTP_400_BAD_REQUEST, "ID mismatch")
    
    try:
        handle_update_location(id, location)
    except Exception as ex:
        raise ex

    return {"status": "success"}

@app.get("/loc/{id}")
async def get_location(id: int):
    try:
        location = await handle_get_location(id)
    except Exception as ex:
        raise ex

    return location

def handle_update_location(id: int, location: Location):
    pass

async def handle_get_location(id: int) -> Location:
    return await db.get_location(id)