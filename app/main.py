from typing import Optional

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/barcode")
def read_barcode(q: str):
    return {"echo": q}


@app.get("/brand_rating")
def read_barcode(q: str):
    return {"echo": q}


@app.post("/logo")
def read_barcode():
    return {"Hello": "world!"}
