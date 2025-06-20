# Dag Definition components
## Library Imports
## DAG arguments
## DAG definition
## Task definitions
## Task pipeline
## Library Imports
from airflow import DAG
from airflow.operators.bash import BashOperator
import datetime as dt

## DAG Arguments
default_args = {
    "owner": "MeloDev",
    "start_date": dt.datetime(2025, 6, 20),  # Today
    "email": "MeloDev@dev.to",
    "email_on_failure": True,
    "email_on_retry": True,
    "retries": 1,
    "retry_delay": dt.timedelta(minutes=5),
}

## DAG Definition
dag = DAG(
    "ETL_toll_data",
    description="Apache Airflow Final Assignment",
    default_args=default_args,
    schedule="@daily",
)

## Task definitions
### Tasks are represented as operators

# Task: Unzip data
task_unzip_data = BashOperator(
    task_id="unzip_data",
    bash_command="tar -xzf ${zip_dir} -C ${target_dir}",
    env={
        "zip_dir": "/opt/airflow/data/tolldata.tgz",
        "target_dir": "/opt/airflow/data/raw/"
    },
    dag=dag,
)

# Task: Extract data from CSV
extract_data_from_csv = BashOperator(
    task_id="extract_data_from_csv",
    # cut utility command extracting rows with delimiter comma specified
    # extract Rowid, Timestamp, Anonymized Vehicle number, Vehicle type
    bash_command="cut -d',' -f1,2,3,4 ${raw_dir}/vehicle-data.csv > ${staging_dir}/csv_data.csv",
    env={
        "raw_dir": "/opt/airflow/data/raw",
        "staging_dir": "/opt/airflow/data/staging"
    },
)

# Task: Extract data from TSV
extract_data_from_tsv = BashOperator(
    task_id='extract_data_from_tsv',
    # extract the fields Number of axles, Tollplaza id, Tollplaza code 
    bash_command="cut -f5,6,7 ${raw_dir}/tollplaza-data.tsv | tr '\t' ',' > ${staging_dir}/tsv_data.csv",
    env={
        "raw_dir": "/opt/airflow/data/raw",
        "staging_dir": "/opt/airflow/data/staging"
    },
)

# Task: Extract data from fixed width file
extract_data_from_fixed_width = BashOperator(
    task_id='extract_data_from_fixed_width',
    # extract the Type of Payment code, Vehicle Code
    bash_command="cut -c 59-62,63-67 ${raw_dir}/payment-data.txt | tr ' ' ',' > ${staging_dir}/fixed_width_data.csv",
    env={
        "raw_dir": "/opt/airflow/data/raw",
        "staging_dir": "/opt/airflow/data/staging"
    },
)

# Task: Consolidate data
consolidate_data = BashOperator(
    task_id='consolidate_data',
    bash_command="""
        paste -d',' ${staging_dir}/csv_data.csv ${staging_dir}/tsv_data.csv ${staging_dir}/fixed_width_data.csv \
        > ${staging_dir}/extracted_data.csv
    """,
    env={
        "staging_dir": "/opt/airflow/data/staging"
    },                
)


# Task 6: Transform vehicle_type to uppercase
transform_data = BashOperator(
    task_id='transform_data',
    bash_command=" awk -F',' 'BEGIN {OFS=\",\"} { $4=toupper($4); print }' "
                    "${staging_dir}/extracted_data.csv > ${staging_dir}/transformed_data.csv",
    env={
        "staging_dir": "/opt/airflow/data/staging"
    },   
)



## Task pipeline
task_unzip_data >> [extract_data_from_csv, extract_data_from_tsv, extract_data_from_fixed_width] >> consolidate_data
consolidate_data >> transform_data
