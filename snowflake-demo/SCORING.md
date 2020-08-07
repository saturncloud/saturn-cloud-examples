# scoring

This document describes code to serve the models used in this demo.

## Scoring Architecture

The code in `run-model.py` implements a thin Flask app to serve the models in this section.

That app assumes that the model has been stored in a `.pkl` file in S3. Deployments must describe which apps to use with the following environment variables.

* `MODEL_BUCKET`: name of an S3 bucket with the model files
* `MODEL_FILE`: key of the model file in that bucket

## Deploying in Saturn

1. Go to the "Jupyter" page and create a new project.
    * `Name`: "test-model-project"
    * `Size`: pick the smallest possible size
    * In `start_script`, add `pip install flask`
    * In `Environment Variables`:
        - `MODEL_BUCKET=saturn-titan`
        - `MODEL_FILE=nyc-taxi/ml_results/models/tip__scikit__elastic_net.pkl`
2. Start that Jupyter. Once it starts, open up Jupyter Lab.
3. In Jupyter, add the deployment code.
    * open a terminal and run `touch /home/jovyan/project/run-model.py`
    * copy the contents of `run-model.py` from this repo into that file and save it
    * after 1 minute, Saturn should automatically snapshot this change and push it to the git repo with your poject code. You'll know this worked if you run `git log -n 3` inside `/home/jovyan/project` and see a recent commit called "snapshot".
4. Close Jupyter Lab. Return to the Saturn UI.
5. Go to the "Deployments" page and create a deployment.
    * `Name`: "tip-model"
    * `Project`: "test-model-project"
    * `Command`: `python /home/jovyan/project/run-model.py`
    * `Instance Count`: 1
    * `Instance Size`: "Medium - 2 cores - 4 GBM RAM"
6. Start the deployment
    * you can watch the sequence of startup events on the "Logs" page
7. Once it's started up, any code running inside Saturn access it! Try that out.
    * return to Jupyter Lab
    * open a Python notebook
    * run this code

    ```python
    import os
    import requests

    MODEL_URL = "https://tip-model-deploy.internal.saturnenterprise.io"
    INFO_ENDPOINT = f"{MODEL_URL}/api/model-info"
    SCORING_ENDPOINT = f"{MODEL_URL}/api/predict"

    SATURN_TOKEN = os.environ["SATURN_TOKEN"]

    result = requests.post(
        url=SCORING_ENDPOINT,
        json={
            "passenger_count": 1,
            "tpep_pickup_datetime": "2019-01-01T11:15:38Z",
            "pickup_taxizone_id": "37",
            "dropoff_taxizone_id": "215"
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": f"{SATURN_TOKEN}"
        }
    )

    result.content
    ```

## Testing Locally

```shell
export MODEL_BUCKET=saturn-titan
export MODEL_FILE=nyc-taxi/ml_results/models/tip__scikit__elastic_net.pkl
```

```shell
from datetime import datetime

payload = {
    "passenger_count": 2,
    "tpep_pickup_datetime": datetime(2019, 1, 1),
    "pickup_taxizone_id": "37",
    "dropoff_taxizone_id": "215"
}

df = pd.DataFrame(payload, index=[0])
```

Get a prediction

```shell
curl -X POST \
    http://0.0.0.0:5090/api/predict \
    -d '{"passenger_count": 1, "tpep_pickup_datetime": "2019-01-01T11:15:38Z", "pickup_taxizone_id": "37", "dropoff_taxizone_id": "215"}'
```

Get information describing the expected input schema and use `jq` to pretty-print it.

```shell
curl -X GET \
    http://0.0.0.0:5090/api/model-info \
    jq .
```
