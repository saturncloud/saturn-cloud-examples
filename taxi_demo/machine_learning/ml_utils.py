import os
import s3fs
import pyarrow.parquet as pq
import pandas as pd

s3 = s3fs.S3FileSystem()

def get_taxi_path() -> str:
    if 'TAXI_S3' not in os.environ:
        raise ValueError('Set TAXI_S3 environment variable to an S3 location that you have read/write access to')
    return os.environ['TAXI_S3']


def read_parquet_dir(path: str) -> pd.DataFrame:
    files = s3.glob(f'{path}/*.parquet')
    return pq.ParquetDataset(files, filesystem=s3).read().to_pandas()


def write_metric_df(taxi_path: str, ml_task: str, tool: str, model: str, rmse: float) -> pd.DataFrame:
    metrics = pd.DataFrame([('tip', 'scikit', 'elastic_net', rmse)], 
                           columns=['ml_task', 'tool', 'model', 'rmse'])
    metrics.to_csv(f'{taxi_path}/ml_results/metrics/{ml_task}__{tool}__{model}.csv', index=False)
    
    return metrics
    