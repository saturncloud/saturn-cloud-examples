# NYC Taxi Demo

This demo contains an end-to-end data analysis and machine learning pipeline using publicly-available data.

## Data 

Yellow taxi trip data from the [NYC Taxi and Limousine Comission (TLC)](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page). The data is [available on S3](https://registry.opendata.aws/nyc-tlc-trip-records-pds/) at `s3://nyc-tlc/`.

The data dictionary for the yellow trip data is available [here](https://www1.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf). Note that this dictionary is for the latest release of data (2019), and the schema/data has changed a few times over the years.

# Components

## ETL and dataset creation

`etl/`
- `etl.ipynb`: collects the CSVs from S3, reconciles schemas, then writes to parquet files
- `ml_datasets.ipynb`: read the parquet files and creates datasets for the machine learning tasks

The ML datasets are for two regression tasks: 
1. Predict total amount of taxi ride in dollars
1. Predict tip percentage (tip amount / total amount) for rides that were paid for with credit cards

## Machine learning

1. Linear models
1. Random Forest
1. XGBoost
1. Model deployment

## Dashboard

The dashboard provides several views of the data across all time, as well as more detailed analysis for recent data. There are visualization of the performance of the different machine learning models as well as a widget for live-scoring new entries.