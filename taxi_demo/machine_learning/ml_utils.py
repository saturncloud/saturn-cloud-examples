import os
import s3fs
import pyarrow.parquet as pq
import pandas as pd
import cloudpickle

s3 = s3fs.S3FileSystem()

def get_taxi_path() -> str:
    if 'TAXI_S3' not in os.environ:
        raise ValueError('Set TAXI_S3 environment variable to an S3 location that you have read/write access to')
    return os.environ['TAXI_S3']


def read_parquet_dir(path: str) -> pd.DataFrame:
    files = s3.glob(f'{path}/*.parquet')
    return pq.ParquetDataset(files, filesystem=s3).read().to_pandas()


def write_model(taxi_path: str, ml_task: str, tool: str, model_name: str, model):
    with s3.open(f'{taxi_path}/ml_results/models/{ml_task}__{tool}__{model_name}.pkl', 'wb') as f:
        cloudpickle.dump(model, f)
    

def write_metric_df(taxi_path: str, ml_task: str, tool: str, model_name: str, metric: str, value: float) -> pd.DataFrame:
    metrics = pd.DataFrame([(ml_task, tool, model_name, metric, value)], 
                           columns=['ml_task', 'tool', 'model', 'metric', 'value'])
    metrics.to_csv(f'{taxi_path}/ml_results/metrics/{ml_task}__{tool}__{model_name}.csv', index=False)
    
    return metrics
    