import datetime
import json
import io
import requests
import polars as pl
from typing import Callable

from openai import OpenAI


def make_llm_request(prompt: str) -> str:
    client = OpenAI(api_key="EMPTY", base_url="http://localhost:8000/v1")

    messages = [
        {"role": "developer", "content": "You are a weather assistant."},
        {"role": "user", "content": prompt},
    ]

    tool_definitions, tool_name_to_func = get_tool_definitions()

    for _ in range(10):
        response = client.chat.completions.create(
            model="",
            messages=messages,
            tools=tool_definitions,
            tool_choice="auto",
            max_completion_tokens=1000,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
        resp_message = response.choices[0].message
        messages.append(resp_message.model_dump())

        print(f"Generated message: {resp_message.model_dump()}")
        print()

        if resp_message.tool_calls:
            for tool_call in resp_message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                func = tool_name_to_func[func_name]
                func_result = func(**func_args)

                messages.append(
                    {
                        "role": "tool",
                        "content": json.dumps(func_result),
                        "tool_call_id": tool_call.id,
                    }
                )
        else:
            return resp_message.content

    last_response = resp_message.content
    return f"Could not resolve request, last response: {last_response}"


def get_tool_definitions() -> tuple[list[dict], dict[str, Callable]]:
    tool_definitions = [
        {
            "type": "function",
            "function": {
                "name": "get_current_date",
                "description": 'Get current date in the format "Year-Month-Day" (YYYY-MM-DD).',
                "parameters": {},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_weather_forecast",
                "description": "Get weather forecast at given country, city, and date.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "country": {
                            "type": "string",
                            "description": "The country the city is in.",
                        },
                        "city": {
                            "type": "string",
                            "description": "The city to get the weather for.",
                        },
                        "date": {
                            "type": "string",
                            "description": (
                                "The date to get the weather for, "
                                'in the format "Year-Month-Day" (YYYY-MM-DD). '
                                "At most 4 weeks into the future."
                            ),
                        },
                    },
                    "required": ["country", "city", "date"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_remote_csv",
                "description": "Read a CSV file from a URL and return a sample of its content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL of the CSV file",
                        },
                    },
                    "required": ["url"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_remote_parquet",
                "description": "Read a Parquet file from a URL and return a sample of its content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL of the Parquet file",
                        },
                    },
                    "required": ["url"],
                },
            },
        },
    ]

    tool_name_to_callable = {
        "get_current_date": current_date_tool,
        "get_weather_forecast": weather_forecast_tool,
        "read_remote_csv": read_remote_csv_tool,
        "read_remote_parquet": read_remote_parquet_tool,
    }

    return tool_definitions, tool_name_to_callable


def current_date_tool() -> str:
    return datetime.date.today().isoformat()


def weather_forecast_tool(country: str, city: str, date: str) -> str:
    if country.lower() in {"united kingdom", "uk", "england"}:
        return "Fog and rain"
    else:
        return "Sunshine"


def read_remote_csv_tool(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()

        df = pl.read_csv(io.BytesIO(response.content), n_rows=50)
        return df.write_json()
    except Exception as e:
        return f"Error reading CSV: {e}"


def read_remote_parquet_tool(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()

        df = pl.read_parquet(io.BytesIO(response.content))
        return df.head(10).write_json()
    except Exception as e:
        return f"Error reading Parquet: {e}"


if __name__ == "__main__":
    prompt = "What will be weather in Birmingham in two weeks?"
    response = make_llm_request(prompt)
    print("Response:\n", response)

    print()

    prompt = "What will be weather in Warsaw the day after tomorrow?"
    response = make_llm_request(prompt)
    print("Response:\n", response)

    print()

    prompt = "What will be weather in New York in two months?"
    response = make_llm_request(prompt)
    print("Response:\n", response)

    print()
    print("[ CSV tool ]")
    csv_url = "https://raw.githubusercontent.com/j-adamczyk/ApisTox_dataset/master/outputs/dataset_final.csv"
    prompt = f"Analyze the CSV file at {csv_url}. What are the columns and what is likely the target variable?"
    response = make_llm_request(prompt)
    print("Response:\n", response)

    print()
    print("[ Parquet tool ]")
    parquet_url = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-01.parquet"
    prompt = f"Check the Parquet file at {parquet_url}. What are the columns and what is likely the target variable?"
    response = make_llm_request(prompt)
    print("Response:\n", response)
