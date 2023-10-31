# Lab 6 - Job ETL - Versão 1

# Imports
import csv
import airflow
import time
import pandas as pd
from datetime import datetime
from datetime import timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.utils.dates import days_ago

# Argumentos
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Cria a DAG
# https://crontab.guru/
dag_lab6_dsa = DAG(dag_id = "lab6",
                   default_args = default_args,
                   schedule_interval = '0 0 * * *',
                   dagrun_timeout = timedelta(minutes = 60),
                   description = 'Job ETL de Carga no DW com Airflow',
                   start_date = airflow.utils.dates.days_ago(1)
)

# Extração de Dados
def extrai_arquivos_csv():
    
    # Lista para os dados no arquivo
    valores = []
    
    # Abre o arquivo em modo leitura
    with open('/opt/airflow/dags/dados/DIM_CLIENTE.csv', 'r') as file:

        # Leitura do arquivo
        reader = csv.reader(file)

        # Loop por cada linha
        for row in reader:
            valores.append(tuple(row))
    
    return valores

# Python Operator (isso serve para que o Airflow consiga executar esse código)
tarefa_leitura_csv = PythonOperator(task_id = 'tarefa_leitura_csv',
                                    python_callable = extrai_arquivos_csv,
                                    dag = dag_lab6_dsa,
)

# Postgres Operator 
tarefa_carrega_dados = PostgresOperator(
    task_id = 'tarefa_carrega_dados',
    sql = 'INSERT INTO lab6.DIM_CLIENTE (id_cliente, nome_cliente, sobrenome_cliente) VALUES (%s, %s, %s)',
    postgres_conn_id = 'Lab6DW',
    params = tarefa_leitura_csv.python_callable(),
    dag = dag_lab6_dsa,
)

# Tarefas Upstream
tarefa_leitura_csv >> tarefa_carrega_dados

# Bloco main
if __name__ == "__main__":
    dag_lab6_dsa.cli()



