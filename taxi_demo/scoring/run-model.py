import boto3
import cloudpickle
import io
import logging
import os
import pandas as pd

from botocore.client import ClientError
from flask import Flask
from flask import jsonify
from flask import request
from marshmallow import fields, Schema

app = Flask(__name__)

logger = logging.getLogger()
logging.basicConfig(
    format="%(levelname)s [%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def _get_env_var(var_name: str) -> str:
    try:
        return os.environ[var_name]
    except KeyError:
        msg = f"Environment variable '{var_name}' must be set"
        logger.fatal(msg)
        raise RuntimeError(msg)


MODEL_BUCKET = _get_env_var("MODEL_BUCKET")
MODEL_FILE = _get_env_var("MODEL_FILE")

logger.info("Fetching model file")
s3 = boto3.client("s3")

stream = io.BytesIO()

try:
    logger.info("Downloading model object")
    s3.download_fileobj(
        Bucket=MODEL_BUCKET,
        Key=MODEL_FILE,
        Fileobj=stream
    )
    logger.info("Successfully downloaded model object")
except ClientError as err:
    msg = "Failed to download model: {}".format(err)
    logger.fatal(msg)
    raise RuntimeError(msg)

logger.info("Deserializing model")
stream.seek(0)
model = cloudpickle.loads(stream.read())
del stream
logger.info("Successfully deserialized model")


class InputSchema(Schema):
    """
    Expected schema for input records. In the future, this
    might be stored along with the model and retrieved at runtime.

    For details on timestamp fields in marshmallow, see
    https://marshmallow.readthedocs.io/en/stable/_modules/marshmallow/fields.html
    """
    passenger_count = fields.Int(required=True)
    tpep_pickup_datetime = fields.DateTime(required=True, format="iso8601")
    pickup_taxizone_id = fields.String(required=True)
    dropoff_taxizone_id = fields.String(require=True)


@app.route('/api/model-info', methods=['GET'])
def get_info():
    """
    Returns the following details that applications using
    the model might need:

    * the expected schema for inputs
    """
    out = {
        "fields": {
            field_name: type(value).__name__
            for field_name, value
            in InputSchema.__dict__["_declared_fields"].items()
        }
    }
    return(jsonify(out))


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    This method expects a JSON payload with the structure
    defined in ``InputSchema``.

    Returns:

    .. code-block:: JSON

        {
            "prediction": <number>
        }
    """
    global model
    payload = InputSchema().loads(request.get_data())
    df = pd.DataFrame(
        data=payload,
        index=[0]
    )

    # add stateless features
    df["pickup_weekday"] = df["tpep_pickup_datetime"].dt.weekday
    df["pickup_weekofyear"] = df["tpep_pickup_datetime"].dt.weekofyear
    df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
    df["pickup_minute"] = df["tpep_pickup_datetime"].dt.minute
    df["pickup_week_hour"] = (df["pickup_weekday"] * 24) + df["pickup_hour"]

    # extra columns are not allowed in sklearn
    del df["tpep_pickup_datetime"]
    pred = model.predict(df)

    return(jsonify({"prediction": pred[0]}))


# NOTE: Saturn only allows deployments over port 8000
#   * https://docs.saturncloud.io/en/articles/3833353-deploying-dashboards
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
