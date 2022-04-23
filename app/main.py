from typing import Optional
from google.cloud import vision
import io

from fastapi import FastAPI, File
from dotenv import load_dotenv
import requests
import os

app = FastAPI()

load_dotenv()

# print(os.getenv("TEST"))

use_mock = 1


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/barcode")
def read_barcode(q: str):
    if(use_mock):
        if(q == "97801401573122"):
            brand = "Apple"
        elif(q == "9780140157375"):
            brand = "Google"
        elif(q == "9780140157374"):
            brand = "Microsoft"
        elif(q == "5449000000966"):
            brand = "Coca Cola Company"
        else:
            brand = "Unknown"
    else:
        url = f"https://api.barcodelookup.com/v3/products?barcode=9780140157376&formatted=y&key={os.getenv('BARCODE_LOOKUP_API_KEY')}"
        r = requests.get(url=url)
        brand = r.json()['products'][0]['brand']
    return {"echo": brand}


@app.get("/brand_rating")
def read_barcode(q: str):
    return {"echo": q}


@app.post("/logo")
def upload_file(file: bytes = File(...)):

    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=file)

    response = client.logo_detection(image=image)
    logos = response.logo_annotations
    logo = logos[0]

    if response.error.message:
        return {"error": f'{response.error.message}'}
    return {"file": logo.description}
