from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(docs_url=None, redoc_url=None)


@app.post("/loc")
def post_loc():
    pass

@app.get("/loc/{id}")
def read_item(id: int):
    return {"id": id}