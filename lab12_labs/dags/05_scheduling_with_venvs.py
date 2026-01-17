import datetime
import json

from airflow import DAG
from airflow.providers.standard.operators.python import (
    PythonOperator,
    PythonVirtualenvOperator,
)


def get_data_venv(data_interval_start_iso: str):
    import os
    import pendulum
    from twelvedata import TDClient
    from dotenv import load_dotenv

    load_dotenv()

    logical_date = pendulum.parse(data_interval_start_iso)
    api_key = os.environ.get("TWELVEDATA_API_KEY")

    td = TDClient(apikey=api_key)
    ts = td.exchange_rate(symbol="USD/EUR", date=logical_date)

    return ts.as_json()


def save_data(data: dict) -> None:
    print("Saving the data")

    if not data:
        raise ValueError("No data")

    with open("/opt/airflow/dags/ex_data.jsonl", "a+") as file:
        file.write(json.dumps(data))
        file.write("\n")


with DAG(
    dag_id="05_scheduling_with_venvs",
    start_date=datetime.datetime(2025, 1, 1),
    schedule=datetime.timedelta(minutes=1),
    catchup=False,
) as dag:
    get_data_op = PythonVirtualenvOperator(
        task_id="get_data",
        python_callable=get_data_venv,
        requirements=["twelvedata", "pendulum", "lazy_object_proxy", "python-dotenv"],
        serializer="cloudpickle",
        op_kwargs={"data_interval_start_iso": "{{ data_interval_start }}"},
        system_site_packages=False,
    )

    save_data_op = PythonOperator(
        task_id="save_data",
        python_callable=save_data,
        op_kwargs={"data": get_data_op.output},
    )

    get_data_op >> save_data_op
