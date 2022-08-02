FROM apache/airflow:2.3.0

WORKDIR /home/phuthu/Desktop/Data Science/Apache Airflow/Demo_Airflow

COPY ./requirement.txt ./requirement.txt

RUN pip install --user --upgrade pip

RUN pip3 install -r requirement.txt

