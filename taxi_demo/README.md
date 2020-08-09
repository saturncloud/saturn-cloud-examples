# NYC Taxi Demo

This demo contains an end-to-end data analysis and machine learning pipeline using publicly-available data, all developed and hosted using Saturn Cloud.

## Quickstart

Create two Jupyter Servers for development, and two Deployments for the dashboard and ML model serving.

#### Jupyter Server: CPU environment

This Jupyter Server sets up and executes most of the pieces of the project:
- Launch CPU Dask cluster
- Data ingestion and ETL
- Exploratory analysis and dashboard development
- Machine learning model training (except GPU/RAPIDS)
- Model scoring API

1. Create Jupyter server
    - Name: `taxi-demo`
    - Disk Space: `100G`
    - Image: Image built with `environment.yml`
    - Environment variables:
        - `TAXI_S3 `: S3 path for all data and model results (i.e. `s3://mybucket/mypath`)
        - `MODEL_FILE`: Filename of model to deploy (i.e. `tip_scikit_xgboost.pkl`)
        - `MODEL_URL`: URL for deployed model (URL field from Saturn Deployment, i.e. `https://taxi-model.demo.saturnenterprise.io`)
1. Launch server, open Jupyter Lab, then open a terminal window to get code
    ```bash
    git clone https://github.com/saturncloud/saturn-cloud-examples.git
    cp -r saturn-cloud-examples/taxi_demo /home/jovyan/project
    ```
1. Ingest data and write files (execute Jupyter notebooks)
    - `etl/etl.ipynb`
    - `etl/ml_datasets.ipynb`
1. Run dashboard EDA and aggregated files
    - `dashboard/data_aggregation.ipynb`
    - See "Dashboard" section below for developing/testing dashboard
1. Run machine learning experiments (except RAPIDS notebooks)
    - `machine_learning/*.ipynb`
1. See "Model Deployment" section below to testing model scoring API


#### Jupyter server: GPU environment: GPU machine learning

This Jupyter Server sets up and executes the machine learning notebooks that utilize GPU Dask clusters.

1. Create Jupyter server
    - Name: `taxi-demo-gpu`
    - Disk Space: `100G`
    - Image: Image built with `gpu_environment.yml`
    - Environment variables:
        - `TAXI_S3 `: S3 path for all data and model results (i.e. `s3://mybucket/mypath`)
1. Launch server, open Jupyter Lab, then get code running the same commands from above
1. Run GPU machine learning experiments
    - `machine_learning/*rapids*.ipynb`



## More details

### Data

Yellow taxi trip data from the [NYC Taxi and Limousine Comission (TLC)](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page). The data is [available on S3](https://registry.opendata.aws/nyc-tlc-trip-records-pds/) at `s3://nyc-tlc/`.

The data dictionary for the yellow trip data is available [here](https://www1.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf). Note that this dictionary is for the latest release of data (2019), and the schema/data has changed a few times over the years.

### Environment / Images

This example will work with images that are included with Saturn, but you can also [build an image yourself](https://www.saturncloud.io/docs/getting-started/setup/customizing-environments/) using the conda environment files provided:

- `environment.yml`: Use this for ETL notebooks, most ML, and dashboard
- `gpu_environment.yml`: Use this for ML tasks that utilize RAPIDS and GPU machines

**TBD**: include pre-built image names here for reference

### Setup Jupyter workspace

To start running this demo inside Saturn Cloud, you can [create a new Jupyter workspace](https://www.saturncloud.io/docs/getting-started/spinning/jupyter/). If you created a custom image, make sure to select it in the "Image" field. Under advanced settings, include the following in the "Start Script" to specify which S3 path to write data to.

```bash
export TAXI_S3='s3://saturn-titan/nyc-taxi'
```

It's important to remember that the image for the Jupyter workspace is re-pulled each time you start it. This means that any package or environment changes you make inside JupyterLab will not be saved once you stop the workspace. Best practice is to include environment setup in a custom image or the start script. All code is managed using Saturn's version control (see below), so your code will always be back when to stop/start the workspace.

If you want to run the machine learning examples that utilize GPUs, you will need to create a new Jupyter workspace using a GPU image.

### Get code

The `project/` folder inside your Jupyter workspace is tracked using [Saturn's version control](https://www.saturncloud.io/docs/collaboration/version-control/), which enables you to collaborate with colleagues on Saturn. If you want to make changes to the demo code, you should copy the folder from the `saturn-cloud-examples` repo into your project folder. Open a new terminal in JupyterLab and run the following (this is a one-time thing and not necessary in the start script):

```bash
git clone https://github.com/saturncloud/saturn-cloud-examples.git
cp -r saturn-cloud-examples/taxi_demo /home/jovyan/project
```

To use a private git repo, [check out this example](https://www.saturncloud.io/docs/connecting/tools/private_git/).

### Credentials

Ensure that you have the [proper S3 credentials configured](https://www.saturncloud.io/docs/connecting/data/) as the code will be writing to the path specified. Alternatively you can refactor the code to read/write from a different data source such as [Snowflake](https://www.saturncloud.io/docs/connecting/data/snowflake/).


### Dask clusters

Dask clusters are configured and launched from within the notebook using the `dask-saturn` package. All worker nodes will utilize the same image and start script configured for the Jupyter server. You can also [manage them from the Saturn UI](https://www.saturncloud.io/docs/getting-started/spinning/dask/#spinning-up-dask-clusters-from-the-ui), and watch the logs on the Logs page.

# Components

## ETL and dataset creation

`etl/`
- `etl.ipynb`: collects the CSVs from S3, reconciles schemas, then writes to parquet files
- `ml_datasets.ipynb`: read the parquet files and creates datasets for the machine learning tasks

The ML datasets are centered around two tasks:
1. "amount": Predict total amount of taxi ride in dollars (regression)
2. "tip": Predict tip percentage (tip amount / total amount) for rides that were paid for with credit cards (regression)
    - This can also be turned into a classification problem where we predict a "high tip" ride (tip percentage >15%)

## Machine learning

There are several items that need to be tracked for the various machine learning experiments, namely:
- `TAXI_S3` S3 file path
- Metadata about which experiment is running
- Trained models (pickle files)
- Test set predictions
- Test set metrics

There is a helper class to avoid repeated code in each notebook: `machine_learning.ml_utils.MLUtils`. Each notebook initializes an `MLUtils` object to keep track of metadata, and to use methods that abstract away some pieces:

```python
from ml_utils import MLUtils

ml_utils = MLUtils(
    ml_task='tip',
    tool='dask',
    model='elastic_net',
)

ml_utils.write_model(...)
ml_utils.write_predictions(...)
```

1. Elastic Net + hyperparameter tuning
1. Random Forest
1. XGBoost

## Model deployment

**TODO**

## Dashboard

The dashboard provides several views of the data across all time, as well as more detailed analysis for recent data. There are visualization of the performance of the different machine learning models as well as a widget for live-scoring new entries. To deploy the dashboard locally do:

```bash
cd dashboard
panel serve dashboard.ipynb
```

In Saturn on the "Deployments" Page start a deployment using the command:

```cd dashboard && python -m panel serve dashboard.ipynb --port=8000 --address="0.0.0.0" --allow-websocket-origin="*"```

## Files

This is the directory structure and files that are written to S3, based on the `TAXI_S3` environment variable.

- `[TAXI_S3]/`
    - `data/`
        - `taxi_parquet/`: Full taxi data in parquet format
            - `_metadata`
            - `part.0.parquet`
            - ...
        - `ml/`: Train/test datasets for ML tasks (parquet)
            - `tip_train/`
            - `tip_test/`
            - ...
        - `dashboard/`: Aggregated data for dashboard (CSV)
    - `ml_results/`: CSV filename format is `[ml task]__[tool]__[model].csv`
        - `predictions/`: Test predictions for each ML model (parquet)
            - `tip__scikit__elastic_net/`
            - `tip__dask__xgboost/`
        - `metrics/`: Summary metrics for each ML model (CSV)
            - `tip__scikit__elastic_net.csv`
            - `tip__dask__xgboost.csv`
            - ...
        - `models/`: Trained models for deployment
            - `tip__scikit__elastic_net.pkl`
            - `tip__dask__xgboost.pkl`
            - ...


# Known issues / troubleshooting

- When trying to immediate read back in a DataFrame written to S3 in parquet with Dask and the `pyarrow` engine, sometimes `pyarrow` gets confused and thinks the files don't exist (`OSError: Passed non-file path: ...`). Restarting the kernel fixes this (or load dataframe in a new notebook).
