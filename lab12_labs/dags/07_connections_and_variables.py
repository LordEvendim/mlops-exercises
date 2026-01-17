import datetime
import os
from airflow import DAG
from airflow.providers.standard.operators.python import (
    PythonOperator,
    PythonVirtualenvOperator,
)
from airflow.providers.postgres.hooks.postgres import PostgresHook

# Had some problems with passing the credentials so I hardcode them in this DAG
os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
os.environ["AWS_ENDPOINT_URL"] = "http://localstack:4566"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


def get_data_venv(data_interval_start_iso: str, api_key: str):
    import pendulum
    from twelvedata import TDClient

    logical_date = pendulum.parse(data_interval_start_iso)

    td = TDClient(apikey=api_key)
    ts = td.exchange_rate(symbol="USD/EUR", date=logical_date)

    return ts.as_json()


def save_to_postgres(data: dict) -> None:
    symbol = data.get("symbol")
    rate = data.get("rate")

    pg_hook = PostgresHook(postgres_conn_id="postgres_data")
    pg_hook.insert_rows(
        table="exchange_rates",
        rows=[(symbol, rate)],
        target_fields=["symbol", "exchange_rate"],
    )
    print(f"Saved {symbol}: {rate} to database.")


with DAG(
    dag_id="07_connections_and_variables",
    start_date=datetime.datetime(2025, 1, 1),
    schedule=datetime.timedelta(minutes=5),
    catchup=False,
    tags=["postgres", "variables"],
) as dag:

    get_data_op = PythonVirtualenvOperator(
        task_id="get_data",
        python_callable=get_data_venv,
        requirements=["twelvedata", "pendulum"],
        serializer="cloudpickle",
        op_kwargs={
            "data_interval_start_iso": "{{ data_interval_start }}",
            "api_key": "{{ var.value.TWELVEDATA_API_KEY }}",
        },
        system_site_packages=False,
    )

    save_op = PythonOperator(
        task_id="save_to_db",
        python_callable=save_to_postgres,
        op_kwargs={"data": get_data_op.output},
    )

    get_data_op >> save_op
