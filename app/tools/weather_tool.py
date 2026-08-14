import requests

from app.llm.gemini import llm


# =========================================================
# GEOCODING
# =========================================================

def geocode_city(
    city: str,
) -> dict | None:

    response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json",
        },
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    results = data.get(
        "results",
        [],
    )

    if not results:
        return None

    location = results[0]

    return {
        "name": location.get(
            "name",
            city,
        ),
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "country": location.get(
            "country",
            "",
        ),
    }


# =========================================================
# WEATHER
# =========================================================

def get_weather(
    city: str,
) -> dict:

    city = (
        city or ""
    ).strip()

    if not city:

        return {
            "answer": (
                "Please specify a city."
            ),
            "sources": [],
        }

    try:

        location = geocode_city(
            city
        )

        if not location:

            return {
                "answer": (
                    f"I couldn't find weather information "
                    f"for {city}."
                ),
                "sources": [],
            }

        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "apparent_temperature,"
                    "precipitation,"
                    "weather_code,"
                    "wind_speed_10m"
                ),
                "timezone": "auto",
            },
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        current = data.get(
            "current",
            {},
        )

        weather_context = f"""
Location: {location['name']}, {location['country']}

Temperature:
{current.get('temperature_2m')} °C

Feels like:
{current.get('apparent_temperature')} °C

Humidity:
{current.get('relative_humidity_2m')} %

Precipitation:
{current.get('precipitation')} mm

Wind speed:
{current.get('wind_speed_10m')} km/h

Weather code:
{current.get('weather_code')}
"""

        prompt = f"""
You are a weather assistant.

CURRENT WEATHER DATA:
{weather_context}

Give the user a short, natural weather response.

Mention:
- temperature
- feels-like temperature
- humidity when useful
- precipitation when useful
- wind when useful

Do not invent weather information.

USER LOCATION:
{city}
"""

        answer = llm.generate(
            prompt
        )

        return {
            "answer": answer,
            "sources": [
                {
                    "title": "Open-Meteo",
                    "url": "https://open-meteo.com/",
                }
            ],
        }

    except Exception as error:

        print(
            "[WEATHER ERROR]",
            repr(error),
        )

        return {
            "answer": (
                "I couldn't retrieve the weather "
                "right now."
            ),
            "sources": [],
        }