import os
from datetime import datetime
import requests
from fastmcp import FastMCP
from dotenv import load_dotenv


load_dotenv()
mcp = FastMCP("OpenWeatherMapMCP")


def fetch_json(url: str, params: dict):
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def geocode(city: str, country: str, api_key: str):
    url = "https://api.openweathermap.org/geo/1.0/direct"
    data = fetch_json(url, {"q": f"{city},{country}", "limit": 1, "appid": api_key})

    return data[0]["lat"], data[0]["lon"]


@mcp.tool(
    description="Daily forecast up to 16 days. Returns summary with temperatures and precipitation."
)
def get_daily_forecast(country: str, city: str, start_date: str, days: int) -> str:
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if days < 1 or days > 16:
        raise ValueError("days must be 1-16")

    lat, lon = geocode(city, country, api_key)
    url = "https://api.openweathermap.org/data/2.5/forecast/daily"
    data = fetch_json(
        url,
        {"lat": lat, "lon": lon, "cnt": days, "units": "metric", "appid": api_key},
    )

    result = []
    for item in data.get("list", []):
        dt = datetime.utcfromtimestamp(item["dt"]).strftime("%Y-%m-%d")
        weather = item.get("weather", [{}])[0].get("description", "")
        temp = item.get("temp", {})
        result.append(
            {
                "date": dt,
                "description": weather,
                "temp_min": temp.get("min"),
                "temp_max": temp.get("max"),
                "precipitation": item.get("rain", 0),
            }
        )

    return str({"start_date": start_date, "days": days, "forecast": result})


@mcp.tool(description="Monthly average weather stats for trips longer than 16 days.")
def get_monthly_weather(country: str, city: str, year: int, month: int) -> str:
    api_key = os.getenv("OPENWEATHER_API_KEY")

    lat, lon = geocode(city, country, api_key)
    url = "https://api.openweathermap.org/data/2.5/forecast/climate"
    data = fetch_json(
        url,
        {
            "lat": lat,
            "lon": lon,
            "month": month,
            "year": year,
            "units": "metric",
            "appid": api_key,
        },
    )

    return str(data)


if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8002)
