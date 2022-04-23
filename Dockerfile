# 
FROM python:3.9
# 
WORKDIR /code
# 
COPY ./requirements.txt /code/requirements.txt
# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
# 
COPY ./app /code/app
# 

COPY dataset.csv /code
# COPY ./cache-gcp-to-csv.py /code/
# CMD ["python", "/code/cache-gcp-to-csv.py"]
#
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker  --threads 8 app.main:app
