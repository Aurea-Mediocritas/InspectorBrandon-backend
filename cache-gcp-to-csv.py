# Download database to CSV

import pandas as pd

from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()
# print(os.getenv("TEST"))

client = bigquery.Client()


def download_data():
    global client
    db_query = """
        SELECT *
        FROM aurea-347907.PhD_ds.emissions
    """
    query_job = client.query(db_query)  # Make an API request.

    query_res = query_job.to_dataframe()
    return query_res


print('Downloading whole db...')
data = download_data()
# data = pd.read_csv('dataset.csv')
# print('\n   Loaded dataset.csv ')
print('   got', len(data), ' rows\n')

print('Dumping')
data.to_csv('dataset.csv')  # Dump database
print('\n  OK')
