# airflow_crawl_and_storage_covid_data

## Part 1: Crawl data and send csv file via email
### 0. Prerequisites
 - `docker, docker-compose, sendgrid` package.
 - `sendgrid` account and `API key`

### 1. Prepare run docker-compose: 
- Add `dags, .env path` into docker-compose.yml at `volumes of x-airflow-common`

### 2. Install html5 and python-dotenv package
#### I try to use `_pip_additional_requirements` in docker-compose.yml but it's not working. So I install them manually:
- step 1: Run all container in docker-compose.yml
    - docker-compose up -d
- step 2: Install package
    - docker exec -it <container_id_airflow_scheduler> bash
    - pip3 install html5 python-dotenv
    - exit
- step 3: Log in airflow account in webserver and run dag
#### I read some suggestions on the website, I decide to build an dockerfile and update docker-compose.yml.
- step 1 : Build a new image based on dockerfile 
    - docker build . --tag <new_name>
- step 2 : Replace image in docker-compose.yml file by new image that you have built.
- step 3 : Run all container in docker-compose
    - docker-compose up -d
    
## Part 2: Load data into Mongodb cloud
### 0. Prerequisites
  - `pymongdb` package
  - Mongodb Atlas account
### 1. Connect to Mongodb Cloud
  - I try to handle `MongoHook` of `aiflow provider` but it's not working. So I use `pymongodb`
  - You only copy the URI on website and pass on source code.
### 2. Issue
  - Although I trying handling `Airflow` and restrict to use another package. But I also newbie in Airflow, I hope you read and comment suggestion or idea for my first project about `Airflow` in order to my project accomplished and smoothly.
