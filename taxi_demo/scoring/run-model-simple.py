import s3fs
import cloudpickle
import os
import pandas as pd
import json
from flask import Flask, jsonify, request

app = Flask(__name__)

TAXI_PATH = os.environ["TAXI_S3"]
MODEL_FILE = os.environ["MODEL_FILE"]

s3 = s3fs.S3FileSystem()
model = cloudpickle.load(s3.open(f's3://{TAXI_PATH}/ml_results/models/{MODEL_FILE}', 'rb'))

features = [
    'pickup_weekday', 
    'pickup_weekofyear', 
    'pickup_hour', 
    'pickup_week_hour', 
    'pickup_minute', 
    'passenger_count',
    'pickup_taxizone_id',
    'dropoff_taxizone_id'
]

@app.route('/api/predict', methods=['POST'])
def predict():
    global model
    payload = json.loads(request.get_data())
    df = pd.DataFrame(data=payload, index=[0])

    # add stateless features
    df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
    df["pickup_weekday"] = df["tpep_pickup_datetime"].dt.weekday
    df["pickup_weekofyear"] = df["tpep_pickup_datetime"].dt.weekofyear
    df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
    df["pickup_minute"] = df["tpep_pickup_datetime"].dt.minute
    df["pickup_week_hour"] = (df["pickup_weekday"] * 24) + df["pickup_hour"]

    pred = model.predict(df[features])
    return(jsonify({"prediction": pred[0]}))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
