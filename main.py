import os
import argparse
import yaml
from dotenv import load_dotenv
from settings import Settings


def export_envs(environment: str = "dev") -> None:
    # ...  # implement me!
    # print(environment)
    env_file = f".env.{environment}"
    if os.path.exists(env_file):
        load_dotenv(env_file)
    else:
        raise ValueError(f"{env_file} does not exist")

    secrets_path = "secrets.yaml"

    with open(secrets_path, "r", encoding="utf-8") as secrets_file:
        data = yaml.safe_load(secrets_file)

    for key, value in data.items():
        os.environ[key] = value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Load environment variables from specified.env file."
    )
    parser.add_argument(
        "--environment",
        type=str,
        default="dev",
        help="The environment to load (dev, test, prod)",
    )
    args = parser.parse_args()

    export_envs(args.environment)

    settings = Settings()

    print("APP_NAME: ", settings.APP_NAME)
    print("ENVIRONMENT: ", settings.ENVIRONMENT)
    print("EXAMPLE_API_KEY: ", settings.EXAMPLE_API_KEY)
