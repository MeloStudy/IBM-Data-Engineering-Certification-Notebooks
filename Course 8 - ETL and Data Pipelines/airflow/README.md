# Command to check the amount of memory available 
```shell
docker run --rm "debian:bookworm-slim" bash -c 'numfmt --to iec $(echo $(($(getconf _PHYS_PAGES) * $(getconf PAGE_SIZE))))' 
```


# Download compose file 
```shell
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/3.0.1/docker-compose.yaml' 
```
or in windows:
```shell
wget 'https://airflow.apache.org/docs/apache-airflow/3.0.1/docker-compose.yaml' -o docker-compose.yaml 
```

# Service definitions 
 - airflow-scheduler - The scheduler monitors all tasks and dags, then triggers the task instances once their dependencies are complete. 
 - airflow-dag-processor - The DAG processor parses DAG files. 
 - airflow-api-server - The api server is available at http://localhost:8080. 
 - airflow-worker - The worker that executes the tasks given by the scheduler. 
 - airflow-triggerer - The triggerer runs an event loop for deferrable tasks. 
 - airflow-init - The initialization service. 
 - postgres - The database. 
 - redis - The redis - broker that forwards messages from scheduler to worker. 
 
 # Create Mounted Directories
 Some directories in the container are mounted, which means that their contents are synchronized between your computer and the container. 
  - ./dags - you can put your DAG files here. 
  - ./logs - contains logs from task execution and scheduler. 
  - ./config - you can add custom log parser or add airflow_local_settings.py to configure cluster policy. 
  - ./plugins - you can put your custom plugins here. 
  
    ```shell
    mkdir ./dags 
    mkdir ./logs 
    mkdir ./plugins 
    mkdir ./config
    ```

# Initializing Environment 
Set airflow uuid as env variable
```shell
echo -e "AIRFLOW_UID=$(id -u)" > .env 
```
manually in windows

## Command to check the id for .env file 
```shell
docker exec --workdir /opt/ -it airflow-airflow-worker-1 sh
```

```shell
id -u 
```

## Initialize airflow.cfg (Optional) 
```shell
docker compose run airflow-cli airflow config list 
```
## Initialize the database 
```shell
docker compose up airflow-init 
```

## Cleaning-up the environment 
```shell
docker compose down --volumes --remove-orphans 
```

# Running Airflow 
```shell
docker compose up
``` 
# Check status
```shell
docker ps
``` 

# Accessing the environment 
After starting Airflow, you can interact with it in 3 ways: 
- by running CLI commands. https://airflow.apache.org/docs/apache-airflow/stable/howto/usage-cli.html 
- via a browser using the web interface. https://airflow.apache.org/docs/apache-airflow/stable/ui.html 
- using the REST API. https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html 

# Running the CLI commands 
```shell
docker compose run airflow-worker airflow info
```
