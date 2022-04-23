import io
import os
import unicodedata

import pandas as pd
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, File
from google.cloud import bigquery, vision

app = FastAPI()

load_dotenv()

BARCODE_API_KEY = os.getenv('BARCODE_LOOKUP_API_KEY')

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
        elif(q == "5449000000996"):
            brand = "Coca-Cola"
        else:
            brand = "Unknown"
    else:
        # q = 9780140157376
        url = f"https://api.barcodelookup.com/v3/products?barcode={q}&formatted=y&key={BARCODE_API_KEY}"
        r = requests.get(url=url)
        brand = r.json()['products'][0]['brand']

    return read_brand_rating(brand)
    # return {"brand_name": brand}


@app.post("/barcode_photo")
def upload_barcode_photo(file: bytes = File(...)):

    raise NotImplementedError()

    image = vision.Image(content=file)

    if response.error.message:
        return {"success": False,
                "error": f'{response.error.message}'}
    else:
        return read_brand_rating(logo.description)
        return {"success": True,
                "name": logo.description}


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


def compare_brand_names(x: str, q: str) -> int:
    "Match query string `q` to brand name `x`."
    # TODO unicode
    def word_split(a):
        for i in " !&'(),-./":
            a = a.replace(i, ' ')
        return a.split()

    x = ' '.join(word_split(x.lower()))
    q = [x for x in word_split(q.lower()) if x != 'company']

    r = [x.find(qq) > -1 for qq in q]
    return r.count(True)  # any(r)

    return x.find(q) > -1


@app.get("/brand_rating")
def read_brand_rating(q: str):
    global data
    # data.to_csv('dataset.csv')  # Dump database
    # print(data.columns)

    # d = data[data["Company_Name_"].str.contains(q)]
    mask = [compare_brand_names(x, q) for x in data["Company_Name_"]]
    mask_max = max(mask)
    d = data[ [(x > 0 and x == mask_max) for x in mask] ]
    count = len(d)
    print(f'[debug] Search str {q}, got {len(d)} row(s)   -- {mask_max=}')

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
    if response.error.message:
        return {"success": False,
                "error": f'{response.error.message}'}

    logos = response.logo_annotations
    if len(logos) == 0:
        return {"success": False,
                "error": "No logos found"}

    logo = logos[0]  # TODO: Error if more than 1 upload?

    print(f'Found OK logo: {logo.description}')
    return read_brand_rating(logo.description)
    # return {"success": True,
    # "name": logo.description}


try:
    # print('Downloading whole db...')
    # data = download_data()
    data = pd.read_csv('dataset.csv')
    print('\n   Loaded dataset.csv ')
    print('   got', len(data), ' rows\n')
except FileNotFoundError as e:
    print(e)
    print('\n dataset.csv not found (DB cache) \n')
