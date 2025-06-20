# Download the data set 
create directory data with sub folders raw,staging and download data using the curl command on the data folder
```shell
wget 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DB0250EN-SkillsNetwork/labs/Final%20Assignment/tolldata.tgz' -o data/tolldata.tgz
```

# Modify Docker-compose.yml volumes to mount data directory
add at `volumes` section
```shell
- ${AIRFLOW_PROJ_DIR:-.}/data:/opt/airflow/data
```

# Exercise: 
Please use the `BashOperator` for all tasks in this assignment.
## Create imports, DAG argument, and definition
1. Create a new file named `ETL_toll_data.py` in `/dags/` directory.
2. Import all the packages you need to build the DAG.
3. Define the DAG arguments as per the following details in the ETL_toll_data.py file:
    - owner             MeloDev
    - start_date        today
    - email             Melo@dev.to
    - email_on_failure	True
    - email_on_retry	True
    - retries	        1 
    - retry_delay	    5 minutes
    
    Take a screenshot of the task code. Name the screenshot `dag_args.jpg`.

4. Define the DAG in the `ETL_toll_data.py` file using the following details.
    - DAG id	        `ETL_toll_data`
    - Schedule	        Daily once
    - default_args	    As you have defined in the previous step
    - description	    Apache Airflow Final Assignment
    
    Take a screenshot of the command and output you used. Name the screenshot `dag_definition.jpg`.

At the end of this exercise, you should have the following screenshots with `.jpg` or `.png` extension:
1. dag_args.jpg
2. dag_definition.jpg

## Create the tasks using BashOperator
### Create a task named `unzip_data` 
task to unzip data. Use the data downloaded in the first part of this assignment and uncompress it into the destination directory using tar.

Take a screenshot of the task code. Name the screenshot `unzip_data.jpg`.

You can locally enter and read through the file fileformats.txt to understand the column details.

### Create a task named `extract_data_from_csv`
task to extract the fields `Rowid, Timestamp, Anonymized Vehicle number, Vehicle type` from the `vehicle-data.csv` file and save them into a file named `csv_data.csv`.

Take a screenshot of the task code. Name the screenshot `extract_data_from_csv.jpg`.

### Create a task named `extract_data_from_tsv` 
task to extract the fields `Number of axles, Tollplaza id, Tollplaza code` from the `tollplaza-data.tsv` file and save it into a file named `tsv_data.csv`.

Take a screenshot of the task code. Name the screenshot `extract_data_from_tsv.jpg`.

### Create a task named `extract_data_from_fixed_width` 
task to extract the fields `Type of Payment code, Vehicle Code` from the fixed width file `payment-data.txt` and save it into a file named `fixed_width_data.csv`.

Take a screenshot of the task code. Name the screenshot `extract_data_from_fixed_width.jpg`.

### Create a task named `consolidate_data` 
task to consolidate data extracted from previous tasks. This task should create a single csv file named `extracted_data.csv` by combining data from the following files:
 - csv_data.csv
 - tsv_data.csv
 - fixed_width_data.csv

The final csv file should use the fields in the order given below:
 - Rowid
 - Timestamp
 - Anonymized Vehicle number
 - Vehicle type
 - Number of axles
 - Tollplaza id
 - Tollplaza code
 - Type of Payment code, and
 - Vehicle Code

Hint: Use the bash paste command that merges the columns of the files passed as a command-line parameter and sends the output to a new file specified. You can use the command man paste to explore more.

Example: paste file1 file2 > newfile

Take a screenshot of the task code. Name the screenshot `consolidate_data.jpg`.

### Create a task named `transform_data` 
task to transform the vehicle_type field in `extracted_data.csv` into capital letters and save it into a file named `transformed_data.csv` in the staging directory.
Hint: You can use the tr command within the BashOperator in Airflow.

Take a screenshot of the task code. Name the screenshot `transform.jpg`.

### Define the task pipeline as per the details given below:
|Task|Functionality|
|-|-|
|First task|unzip_data|
|Second task|extract_data_from_csv|
|Third task|extract_data_from_tsv|
|Fourth task|extract_data_from_fixed_width|
|Fifth task|consolidate_data|
|Sixth task|transform_data|

Take a screenshot of the task pipeline section of the DAG. Name the screenshot `task_pipeline.jpg`.

At the end of this exercise, you should have the following screenshots with .jpg or .png extension:
- unzip_data.jpg
- extract_data_from_csv.jpg
- extract_data_from_tsv.jpg
- extract_data_from_fixed_width.jpg
- consolidate_data.jpg
- transform.jpg
- task_pipeline.jpg

## Getting the DAG operational
1. Submit the DAG. Use CLI or Web UI to show that the DAG has been properly submitted. Take a screenshot showing that the DAG you created is in the list of DAGs. Name the screenshot `submit_dag.jpg`.

Note: If you don't find your DAG in the list, you can check for errors using the following command in the terminal:
```shell
docker exec --workdir /opt/ -it airflow-airflow-worker-1 sh
```
```shell
airflow dags list-import-errors
```

2. Unpause and trigger the DAG through CLI or Web UI.
3. Take a screenshot of DAG unpaused on CLI or the GUI. Name the screenshot `unpause_trigger_dag.jpg`.
4. Take a screenshot of the tasks in the DAG run through CLI or Web UI. Name the screenshot `dag_tasks.jpg`.
5. Take a screenshot the DAG runs for the Airflow console through CLI or Web UI. Name the screenshot `dag_runs.jpg`.

### Screenshot checklist
You should have the following screenshots with .jpg or .png extension:
- submit_dag.jpg
- unpause_trigger_dag.jpg
- dag_tasks.jpg
- dag_runs.jpg

This action concludes the assignment.