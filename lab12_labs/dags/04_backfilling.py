import datetime
import pandas as pd
import requests

import pendulum

from airflow.providers.standard.operators.python import PythonOperator
from airflow import DAG


def get_weather_forecast(**kwargs) -> dict:
    logical_date: pendulum.DateTime = kwargs["logical_date"]
    params = {
        "latitude": 40.7127,
        "longitude": -74.0059,
        "start_date": logical_date.format("YYYY-MM-DD"),
        "end_date": (logical_date + datetime.timedelta(days=6)).format("YYYY-MM-DD"),
        "daily": ["temperature_2m_max", "temperature_2m_min"],
        "timezone": "America/New_York",
    }

    response = requests.get(
        "https://archive-api.open-meteo.com/v1/archive", params=params
    )

    response.raise_for_status()

    return response.json()


def save_weather_data(data: dict) -> None:
    daily_data = data["daily"]
    df = pd.DataFrame(
        {
            "date": daily_data["time"],
            "temp_min": daily_data["temperature_2m_min"],
            "temp_max": daily_data["temperature_2m_max"],
        }
    )

    output_file = "/opt/airflow/dags/data.jsonl"
    with open(output_file, "a") as f:
        header = f.tell() == 0
        df.to_csv(f, header=header, index=False)
        print(f"Saved {len(df)} rows")


with DAG(
    dag_id="04_backfilling_weather",
    start_date=datetime.datetime(2025, 1, 1),
    end_date=datetime.datetime(2025, 1, 31),
    schedule=datetime.timedelta(days=7),
    catchup=True,
) as dag:

    get_weather_op = PythonOperator(
        task_id="get_weather", python_callable=get_weather_forecast
    )

    save_weather_op = PythonOperator(
        task_id="save_weather",
        python_callable=save_weather_data,
        op_kwargs={"data": get_weather_op.output},
    )

    get_weather_op >> save_weather_op
