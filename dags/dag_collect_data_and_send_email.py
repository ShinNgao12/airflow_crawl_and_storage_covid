import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import time
import datetime
import os
from dotenv import load_dotenv

from airflow import DAG
from airflow.operators.python import PythonOperator

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)
import base64

load_dotenv('/opt/airflow/.env')

header = ['#', 'Country,Other', 'TotalCases','NewCases','TotalDeaths','NewDeaths',
              'TotalRecovered' , 'NewRecovered' , 'ActiveCases' , 'Serious,Critical' , 
              'Tot Cases/1M pop', 'Deaths/1M pop', 'TotalTests', 'Tests/1M pop', 'Population',
              'Continent', 'New Cases/1M pop', 'New Deaths/1M pop', 'Active Cases/1M pop'] 

url =  'https://www.worldometers.info/coronavirus/'

def collect_yesterday(yesterday):
    data_dict = {}
    while True:
        for i in header:
            data_dict[i] = []  

        re = requests.get(url)
        soup = BeautifulSoup(re.text, 'html5lib')
        source = soup.find('table', {'id' :"main_table_countries_yesterday"})
        data = source.tbody.text

        # tách dữ liệu
        data = data.split('\n'*13)[-1]

        # chuyển dữ liệu thành dictionary 
        lines = data.split('\n')
        idx = 0
        while (idx < len(lines)):
            att = idx % 23
            if att in [16,17,21,22]:
                idx += 1
                continue
            elif lines[idx] == '' or lines[idx] == 'N/A':
                if att > 15:
                    data_dict[header[att - 2]].append(np.nan)
                    idx += 1
                else:
                    data_dict[header[att]].append(np.nan)
                    idx += 1
            else:
                if att > 15 :
                    data_dict[header[att - 2]].append(lines[idx])
                    idx += 1
                else:
                    data_dict[header[att]].append(lines[idx])
                    idx += 1
                    
        length = min([len(v) for k, v in data_dict.items()])
        if len(data_dict['#']) == length and data_dict['#'][-1] != np.nan:
            break
        time.sleep(0.5)

    yesterday_df = pd.DataFrame(data_dict).set_index('#')
    yesterday_df['Date'] = yesterday
    yesterday_df.replace(' ', np.nan, inplace = True)
    # write to csv
    # refer: https://www.reddit.com/r/docker/comments/ow3j8la/comment/h7dz138/
    yesterday_df.to_csv(f'/opt/airflow/data/covid_{yesterday}.csv', index = False)
    return True

def tranform(yesterday):
    # load data)
    yesterday_df = pd.read_csv(f'/opt/airflow/data/covid_{yesterday}.csv')
    
    # clean numerical data
    yesterday_df.replace(r'\s{2,}',np.nan,inplace = True, regex=True)
    yesterday_df.replace('N/A', np.nan, inplace = True,regex = True)
    yesterday_df.replace(',','', inplace = True, regex = True)
    yesterday_df.replace('\+','', inplace = True, regex = True)

    # convert dtypes
    def convert_to_numeric(col):
        try:
            col = col.str.strip()
            col = col.astype('float64')
        finally:
            return col
        
    yesterday_df = yesterday_df.apply(convert_to_numeric)
    yesterday_df['Date'] = pd.to_datetime(yesterday_df['Date'], format = '%Y-%m-%d')

    # clean categorical data
    yesterday_df['Country,Other'] = yesterday_df['Country,Other'].str.strip()
    yesterday_df['Continent'] = yesterday_df['Continent'].str.strip()
    yesterday_df = yesterday_df[yesterday_df['Continent'].notna()]
    yesterday_df.to_csv(f'/opt/airflow/data/covid_{yesterday}.csv', index = False)

    return True

def send_mail(yesterday):
    messenger = Mail(
        from_email=os.getenv('FROM_EMAIL'),
        to_emails=os.getenv('TO_EMAIL'),
        subject = f'Covid {yesterday}',
        html_content=f'<h2>THE SITUATION COVID-19 {yesterday}</h2>'
    )
    with open(f'/opt/airflow/data/covid_{yesterday}.csv', 'rb') as f:
        data = f.read()
        f.close()

    encoded_file = base64.b64encode(data).decode()

    attachedFile = Attachment(
        FileContent(encoded_file),
        FileName(f'covid_{yesterday}.csv'),
        FileType('text/csv'),
        Disposition('attachment')                                                                                                                                                                                                               
    )
    messenger.attachment = attachedFile

    try:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
        sg = SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
        response = sg.send(messenger)
        print(response.status_code)                                                                 
        print(response.body)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
        print(response.headers)
        print(datetime.datetime.now())
        
    except Exception as e:
        print(e.message)

    return True

default_args = {
    'owner':'phuthu',
    'retries': 5,
    'retry_delay': datetime.timedelta(minutes = 2)
}

with DAG(
    dag_id = 'dag_collect_data_and_send_email_ver_final',
    start_date = datetime.datetime(2022,8,1,0),
    schedule_interval = '@daily',
    default_args = default_args
) as dag:
    crawl_task = PythonOperator(
        task_id = 'collect_data',
        python_callable = collect_yesterday,
        op_kwargs = {"yesterday" : '{{ yesterday_ds }}'}
    )

    transform_task = PythonOperator(
        task_id = 'tranform_data',
        python_callable = tranform,
        op_kwargs = {"yesterday" : '{{ yesterday_ds }}'}
    )

    send_email = PythonOperator(
        task_id ='send_email',
        python_callable= send_mail,
        op_kwargs={"yesterday" : '{{ yesterday_ds }}'}
    )

    crawl_task >> transform_task >> send_email


