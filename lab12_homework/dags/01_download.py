from datetime import datetime
from airflow.decorators import dag, task
from config import (
    S3_BUCKET_PROCESSED,
    S3_BUCKET_RAW,
    S3_CLIENT_OPTIONS,
    API_URL,
    LATITUDE,
    LONGITUDE,
)


@dag(
    dag_id="01_download_weather_data",
    start_date=datetime(2025, 1, 1),
    schedule="@monthly",
    catchup=True,
    max_active_runs=1,
)
def download_data_pipeline():
    @task.virtualenv(
        task_id="download_raw_data",
        requirements=["requests", "s3fs"],
        python_version="3.11",
        system_site_packages=False,
    )
    def download_to_s3(
        fetch_start_date: str,
        fetch_end_date: str,
        lat: float,
        lon: float,
        bucket: str,
        storage_options: dict,
        api_url: str,
    ) -> str:
        import json
        import requests
        import s3fs
        from datetime import date, datetime, timedelta

        if datetime.strptime(fetch_end_date, "%Y-%m-%d").date() >= date.today():
            fetch_end_date = (date.today() - timedelta(days=5)).strftime("%Y-%m-%d")

        daily_vars = [
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "relative_humidity_2m_mean",
            "cloud_cover_mean",
            "surface_pressure_mean",
            "wind_speed_10m_max",
            "precipitation_sum",
        ]

        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": fetch_start_date,
            "end_date": fetch_end_date,
            "daily": daily_vars,
            "timezone": "auto",
        }

        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()

        fs = s3fs.S3FileSystem(**storage_options)
        fs.mkdirs(bucket, exist_ok=True)

        month_str = fetch_start_date[:7]
        filename = f"weather_{month_str}.json"
        s3_path = f"s3://{bucket}/{filename}"

        with fs.open(s3_path, "w") as f:
            json.dump(data, f)

        return s3_path

    @task.virtualenv(
        task_id="process_data",
        requirements=["polars", "s3fs", "fsspec", "pyarrow"],
        python_version="3.11",
        system_site_packages=False,
    )
    def process_data_polars(
        raw_s3_path: str, bucket_out: str, storage_options: dict
    ) -> str:
        import polars as pl
        import s3fs
        import json

        fs = s3fs.S3FileSystem(**storage_options)
        fs.mkdirs(bucket_out, exist_ok=True)

        with fs.open(raw_s3_path, "rb") as f:
            json_data = json.load(f)

        df = pl.DataFrame(json_data.get("daily", {})).select(
            pl.col("time").str.to_date().alias("date"),
            pl.exclude("time").cast(pl.Float64),
        )

        file_name = raw_s3_path.split("/")[-1].replace(".json", ".parquet")
        out_path = f"s3://{bucket_out}/{file_name}"

        with fs.open(out_path, "wb") as f:
            df.write_parquet(f)

        return out_path

    raw_path = download_to_s3(
        fetch_start_date="{{ data_interval_start.start_of('month').to_date_string() }}",
        fetch_end_date="{{ data_interval_start.end_of('month').to_date_string() }}",
        lat=LATITUDE,
        lon=LONGITUDE,
        bucket=S3_BUCKET_RAW,
        storage_options=S3_CLIENT_OPTIONS,
        api_url=API_URL,
    )

    process_data_polars(
        raw_s3_path=raw_path,
        bucket_out=S3_BUCKET_PROCESSED,
        storage_options=S3_CLIENT_OPTIONS,
    )


download_data_pipeline()
