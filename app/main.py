from typing import Optional
from google.cloud import bigquery, vision
import io

from fastapi import FastAPI, File
from dotenv import load_dotenv
import requests
import os

import pandas as pd

app = FastAPI()

load_dotenv()

# print(os.getenv("TEST"))

use_mock = 1


# client = bigquery.Client()


# def download_data():   # Use cache-gcp-to-csv.py
#     global client
#     db_query = """
#         SELECT *
#         FROM aurea-347907.PhD_ds.emissions
#     """
#     query_job = client.query(db_query)  # Make an API request.

#     query_res = query_job.to_dataframe()
#     return query_res


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
        else:
            brand = "Unknown"
    else:
        url = f"https://api.barcodelookup.com/v3/products?barcode=9780140157376&formatted=y&key={os.getenv('BARCODE_LOOKUP_API_KEY')}"
        r = requests.get(url=url)
        brand = r.json()['products'][0]['brand']

    return {"brand_name": brand}


USABLE_COLS = ["Company_Name_",
               "Account_Number", "Country_",
               "Reporting_Year", "Ticker_Symbol_",
               "ISIN_",
               "Disclosure_Score", "Performance_Band",
               "Response_Status",
               "Scope_1__metric_tonnes_CO2e_",
               "Scope_2__metric_tonnes_CO2e_",
               "Country_Location",
               ]
# ValueError: Out of range float values are not JSON compliant
#    "Parent_Account_", "Permission",


def compare_brand_names(x: str, q: str):
    # TODO unicode
    x = x.lower()
    q = q.lower()
    return x.find(q) > -1


@app.get("/brand_rating")
def read_brand_rating(q: str):
    global data
    # data.to_csv('dataset.csv')  # Dump database
    # print(data.columns)

    # d = data[data["Company_Name_"].str.contains(q)]
    mask = [compare_brand_names(x, q) for x in data["Company_Name_"]]
    d = data[mask]
    count = len(d)
    print(f'[debug] Search str {q}, got {len(d)} row(s)')

    if count == 0:
        return {"success": False, "error": "Not found"}
    elif count == 1:
        # return list(d.columns)
        d = d.to_dict()

        d = {k: v for k, v in d.items() if k in USABLE_COLS}

        # column value: {140: } -- pandas index?
        d = {k: list(v.values())[0] for k, v in d.items()}

        return {"success": True,
                "brand_rating": d}
    else:
        return {"success": False,
                "Possible_names": d['Company_Name_'].to_list()}


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


try:
    # print('Downloading whole db...')
    # data = download_data()
    data = pd.read_csv('dataset.csv')
    print('\n   Loaded dataset.csv ')
    print('   got', len(data), ' rows\n')
except FileNotFoundError as e:
    print(e)
    print('\n dataset.csv not found (DB cache) \n')
