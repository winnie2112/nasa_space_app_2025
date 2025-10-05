import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

from statsmodels.tsa.holtwinters import ExponentialSmoothing

from datetime import date
from dateutil.relativedelta import relativedelta

# test variables
latitude = 52.52
longitude = 13.41
specified_date = date(2025, 10, 19)

def calculate_forecast(latitude, longitude, specified_date):
    last_updated_date = date.today() - relativedelta(days=5) # Docs say 5 day lag but in reality less date(2025, 10, 2)

    future_days = (specified_date - last_updated_date).days

    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": (last_updated_date - relativedelta(years=10)).strftime("%Y-%m-%d"),
        "end_date": last_updated_date.strftime("%Y-%m-%d"),
        "daily": ["rain_sum", "temperature_2m_mean"],
        "timezone": "auto",
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation: {response.Elevation()} m asl")
    print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_rain_sum = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_mean = daily.Variables(1).ValuesAsNumpy()

    # Create Pandas DataFrame
    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}

    daily_data["rain_sum"] = daily_rain_sum
    daily_data["temperature_2m_mean"] = daily_temperature_2m_mean

    daily_dataframe = pd.DataFrame(data = daily_data)
    daily_dataframe["date"] = pd.to_datetime(daily_dataframe["date"]).dt.tz_convert(None)
    daily_dataframe = daily_dataframe.set_index("date")

    # baseline
    print(f"baseline: {daily_dataframe[(daily_dataframe.index.month==specified_date.month) & (daily_dataframe.index.day == specified_date.day)].mean()}")

    # Holt Winter Exponential Smoothing
    temp_model = ExponentialSmoothing(daily_data["temperature_2m_mean"], seasonal="add", seasonal_periods=365).fit(0.0, 0.2, 0.1)
    temp_forecast = temp_model.forecast(steps=future_days)

    rain_model = ExponentialSmoothing(daily_data["rain_sum"], seasonal="add", seasonal_periods=365).fit(0.1, 0.3, 0.3)
    rain_forecast = rain_model.forecast(steps=future_days)

    print(f"{[(temp, rain) for (temp, rain) in zip(temp_forecast, rain_forecast)]}")

    return {
        "Temperature": temp_forecast[-1],
        "Rainfall": rain_forecast[-1],
        "Chance of Rain": min(rain_forecast[-1] * 10, 100),
        "Max Temperature of Day": temp_forecast[-1],
        "Min Temperature of Day": temp_forecast[-1],
        "Wind Speed": -1,
        "Chance of Rain": -1,
        "Cloud Cover": 0,
        "Sum snowfall": 0, # hourly sum of snowfall in centimeters
        "UV Index": 0,
    }

