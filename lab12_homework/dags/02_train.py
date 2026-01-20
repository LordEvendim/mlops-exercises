from datetime import datetime
from airflow.decorators import dag, task
from config import (
    S3_BUCKET_PROCESSED,
    S3_BUCKET_MODELS,
    S3_CLIENT_OPTIONS,
    POSTGRES_CONN_ID,
)


@dag(
    dag_id="02_train_models",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
)
def train_models_pipeline():
    @task.virtualenv(
        task_id="prepare_dataset",
        requirements=["polars", "s3fs", "fsspec", "pyarrow", "pendulum"],
        python_version="3.11",
        system_site_packages=False,
    )
    def prepare_dataset(bucket_in: str, storage_options: dict) -> dict:
        import polars as pl
        import s3fs

        fs = s3fs.S3FileSystem(**storage_options)
        files = fs.glob(f"{bucket_in}/*.parquet")
        file_paths = [f"s3://{f}" for f in files]
        df = pl.scan_parquet(file_paths).collect().sort("date")

        max_date = df["date"].max()
        split_date = max_date.replace(day=1)
        print(f"Splitting data at {split_date}")

        train_df = df.filter(pl.col("date") < split_date)
        test_df = df.filter(pl.col("date") >= split_date)

        if train_df.height == 0 or test_df.height == 0:
            raise ValueError("Training or Test set is empty.")

        target = "precipitation_sum"

        return {
            "X_train": train_df.drop(["date", target]).to_dicts(),
            "X_test": test_df.drop(["date", target]).to_dicts(),
            "y_train": train_df.select(target).to_series().to_list(),
            "y_test": test_df.select(target).to_series().to_list(),
            "train_rows": train_df.height,
        }

    @task.virtualenv(
        task_id="train_ridge",
        requirements=["scikit-learn", "polars", "joblib", "pandas", "s3fs"],
        python_version="3.11",
    )
    def train_ridge(dataset: dict, bucket_models: str, storage_options: dict) -> dict:
        import polars as pl
        import s3fs
        import joblib
        from sklearn.linear_model import Ridge
        from sklearn.metrics import mean_absolute_error

        X_train = pl.DataFrame(dataset["X_train"]).to_pandas()
        X_test = pl.DataFrame(dataset["X_test"]).to_pandas()
        y_train = dataset["y_train"]
        y_test = dataset["y_test"]

        model = Ridge(alpha=1.0)
        model.fit(X_train, y_train)

        mae = mean_absolute_error(y_test, model.predict(X_test))

        fs = s3fs.S3FileSystem(**storage_options)
        model_name = "ridge_regression"
        local_path = f"/tmp/{model_name}.joblib"
        s3_path = f"s3://{bucket_models}/temp/{model_name}.joblib"

        joblib.dump(model, local_path)
        fs.put(local_path, s3_path)

        return {
            "model_name": model_name,
            "mae": mae,
            "s3_path": s3_path,
            "train_size": dataset["train_rows"],
        }

    @task.virtualenv(
        task_id="train_rf",
        requirements=["scikit-learn", "polars", "joblib", "numpy", "pandas", "s3fs"],
        python_version="3.11",
    )
    def train_rf(dataset: dict, bucket_models: str, storage_options: dict) -> dict:
        import polars as pl
        import s3fs
        import joblib
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.model_selection import RandomizedSearchCV
        from sklearn.metrics import mean_absolute_error

        X_train = pl.DataFrame(dataset["X_train"]).to_pandas()
        X_test = pl.DataFrame(dataset["X_test"]).to_pandas()
        y_train = dataset["y_train"]
        y_test = dataset["y_test"]

        param_dist = {"n_estimators": [50, 100], "max_depth": [10, 20]}
        rf = RandomForestRegressor(random_state=42)
        search = RandomizedSearchCV(rf, param_dist, n_iter=2, cv=3, n_jobs=-1)
        search.fit(X_train, y_train)

        mae = mean_absolute_error(y_test, search.best_estimator_.predict(X_test))

        fs = s3fs.S3FileSystem(**storage_options)
        model_name = "random_forest"
        local_path = f"/tmp/{model_name}.joblib"
        s3_path = f"s3://{bucket_models}/temp/{model_name}.joblib"

        joblib.dump(search.best_estimator_, local_path)
        fs.put(local_path, s3_path)

        return {
            "model_name": model_name,
            "mae": mae,
            "s3_path": s3_path,
            "train_size": dataset["train_rows"],
        }

    @task.virtualenv(
        task_id="train_svm",
        requirements=["scikit-learn", "polars", "joblib", "pandas", "s3fs"],
        python_version="3.11",
    )
    def train_svm(dataset: dict, bucket_models: str, storage_options: dict) -> dict:
        import polars as pl
        import s3fs
        import joblib
        from sklearn.svm import SVR
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import mean_absolute_error

        X_train = pl.DataFrame(dataset["X_train"]).to_pandas()
        X_test = pl.DataFrame(dataset["X_test"]).to_pandas()
        y_train = dataset["y_train"]
        y_test = dataset["y_test"]

        model = make_pipeline(StandardScaler(), SVR(C=1.0, epsilon=0.2))
        model.fit(X_train, y_train)

        mae = mean_absolute_error(y_test, model.predict(X_test))

        fs = s3fs.S3FileSystem(**storage_options)
        model_name = "svm_regressor"
        local_path = f"/tmp/{model_name}.joblib"
        s3_path = f"s3://{bucket_models}/temp/{model_name}.joblib"

        joblib.dump(model, local_path)
        fs.put(local_path, s3_path)

        return {
            "model_name": model_name,
            "mae": mae,
            "s3_path": s3_path,
            "train_size": dataset["train_rows"],
        }

    @task.virtualenv(
        task_id="select_best_model",
        requirements=["s3fs"],
        python_version="3.11",
        system_site_packages=False,
    )
    def select_best(results: list, bucket_models: str, storage_options: dict) -> str:
        import s3fs

        best_result = min(results, key=lambda x: x["mae"])
        print(f"Best Model: {best_result['model_name']} with MAE: {best_result['mae']}")

        fs = s3fs.S3FileSystem(**storage_options)

        best_path_dest = f"s3://{bucket_models}/best_model.joblib"
        fs.copy(best_result["s3_path"], best_path_dest)

        for res in results:
            if fs.exists(res["s3_path"]):
                fs.rm(res["s3_path"])

        return best_result["model_name"]

    @task
    def log_results_to_postgres(results: list, conn_id: str):
        from airflow.providers.postgres.hooks.postgres import PostgresHook

        hook = PostgresHook(postgres_conn_id=conn_id)
        rows = [(res["model_name"], res["train_size"], res["mae"]) for res in results]

        hook.insert_rows(
            table="model_performance",
            rows=rows,
            target_fields=["model_name", "training_set_size", "test_mae"],
        )

    # Prepare
    dataset = prepare_dataset(
        bucket_in=S3_BUCKET_PROCESSED, storage_options=S3_CLIENT_OPTIONS
    )

    # Train (Fan-out)
    ridge_res = train_ridge(dataset, S3_BUCKET_MODELS, S3_CLIENT_OPTIONS)
    rf_res = train_rf(dataset, S3_BUCKET_MODELS, S3_CLIENT_OPTIONS)
    svm_res = train_svm(dataset, S3_BUCKET_MODELS, S3_CLIENT_OPTIONS)

    results = [ridge_res, rf_res, svm_res]

    # Fan-in
    select_best(results, S3_BUCKET_MODELS, S3_CLIENT_OPTIONS)
    log_results_to_postgres(results, POSTGRES_CONN_ID)


train_models_pipeline()
