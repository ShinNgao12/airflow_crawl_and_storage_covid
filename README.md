# airflow_crawl_and_storage_covid_data

## Part 1: Crawl data and send csv file via email
### 0. Prerequisites
 - docker, docker-compose, sendgrid package.
 - sendgrid account and API key

### 1. Prepare run docker-compose: 
- Add `dags, .env path` into docker-compose.yml at `volumes of x-airflow-common`

### 2. Install html5 and python-dotenv package
#### I try to use `_pip_additional_requirements` in docker-compose file but It's not working. So I install them manually:
- step 1: run all container in docker-compose.yml
    - docker-compose up -d
- step 2: install package
    - docker exec -it <container_id_airflow_scheduler> bash
    - pip3 install html5 python-dotenv
    - exit
- step 3: Log in airflow account in webserver and run dag
#### I read some suggestions on the website, I decide to build an dockerfile and update docker-compose.yml.
- step 1 : build a new dockerfile
    docker build . --tag <new_name>
- step 2 : replace image in docker-compose.yml file by new name image that you have built.
- step 3 : run all container in docker-composes
    docker-compose up -d
