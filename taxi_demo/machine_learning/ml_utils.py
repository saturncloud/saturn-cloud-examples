import os
import s3fs
import pyarrow.parquet as pq
import pandas as pd
import numpy as np
import cloudpickle

s3 = s3fs.S3FileSystem()

class TipVars(object):
    """
    Features and other variables for the tip prediction task
    """
    numeric_feat = [
        'pickup_weekday', 
        'pickup_weekofyear', 
        'pickup_hour', 
        'pickup_week_hour', 
        'pickup_minute', 
        'passenger_count',
    ]
    categorical_feat = [
        'pickup_taxizone_id', 
        'dropoff_taxizone_id',
    ]
    features = numeric_feat + categorical_feat
    y_col = 'tip_fraction'
    high_tip = 0.25
    y_clf = 'high_tip'


    elastic_net_grid_search_params = {
        'clf__l1_ratio': np.arange(0, 1.01, 0.01),
        'clf__alpha': [0, 0.5, 1, 2],
    }
    

class MLUtils(object):
    """
    Helper class to keep track of which task/tool/model is running, 
    as well as several methods to do save results.
    
    This class should not abstract away any major functionality that should be highlighted for comparing
    the different tools. It serves mostly to simplify the "boring" pieces that aren't related
    to illustrating performance differences between single-node Python, Dask, Spark, and/or RAPIDS.
    """
    
    def __init__(self, ml_task, tool, model):
        self.ml_task = ml_task
        self.tool = tool
        self.model = model
        self.tip_vars = TipVars()
        self.taxi_path = self.get_taxi_path()

    def get_taxi_path(self) -> str:
        """
        Check that the TAXI_S3 environment variable is set
        """
        if 'TAXI_S3' not in os.environ:
            raise ValueError('Set TAXI_S3 environment variable to an S3 location that you have read/write access to')
        return os.environ['TAXI_S3']

    def read_parquet_dir(self, path: str) -> pd.DataFrame:
        """
        Helper function for pandas to read a directory of parquet files
        """
        files = s3.glob(f'{path}/*.parquet')
        return pq.ParquetDataset(files, filesystem=s3).read().to_pandas()

    def write_model(self, model) -> None:
        """
        Write a trained model to S3 (technically works with any cloudpickle-able object).
        """
        s3_key = f'{self.taxi_path}/ml_results/models/{self.ml_task}__{self.tool}__{self.model}.pkl'
        print(f"uploading model to '{s3_key}'")
        with s3.open(s3_key, 'wb') as f:
            cloudpickle.dump(model, f)
        print("successfully uploaded model")

    def write_predictions(self, df, rm=True):
        """
        Write a parquet file with model predictions on the test set
        """
        path = f'{self.taxi_path}/ml_results/predictions/{self.ml_task}__{self.tool}__{self.model}'
        print(f"Writing predictions to '{path}'")
        if rm and s3.exists(path):
            s3.rm(path, recursive=True)

        if type(df) == pd.DataFrame:
            df.to_parquet(f'{path}/0.parquet', index=False)
        else:
            df.to_parquet(path, engine='pyarrow', compression='snappy')
        print("Done writing predictions")

    def write_metric_df(self, metric: str, value: float) -> pd.DataFrame:
        """
        Write a CSV with summary metrics for models evaluated on the test set
        """
        metrics = pd.DataFrame([(self.ml_task, self.tool, self.model, metric, value)], 
                               columns=['ml_task', 'tool', 'model', 'metric', 'value'])
        metrics.to_csv(f'{self.taxi_path}/ml_results/metrics/{self.ml_task}__{self.tool}__{self.model}.csv', index=False)

        return metrics
