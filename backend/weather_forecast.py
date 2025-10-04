"""Backend to fetch weather data from API."""

from zoneinfo import ZoneInfo
from datetime import datetime
from dataclasses import dataclass

from typing import Dict, Any, Callable, List, Tuple
import requests


IP_LOCATION_API = "http://ip-api.com/json/"
WEATHER_API = "https://api.open-meteo.com/v1/forecast"
RETRIEVE_LOCAL = "https://geocoding-api.open-meteo.com/v1/search"
MODEL_MAP = {
    "ECMWF IFS": "ecmwf_ifs",
    "NOAA GFS": "gfs_seamless",
    "DWD ICON": "icon_global",
    "Météo-France": "arpege_world"
}

def fetch_api_data(
    url: str,
    params: Dict[str, Any] | None = None,
    error_msg: Callable[[str], None] | None = None,
) -> Any | None:
    """Helper function to fetch data from an API."""
    try:
        resp = requests.get(url, params=params)
        if resp.status_code == 429:  # Too Many Requests
            if error_msg:
                error_msg("Rate limit exceeded: Too many requests (429).")
            return None
        resp.raise_for_status()
        return resp.json()
    except (RuntimeError, requests.RequestException) as errors:
        if error_msg:
            error_msg(str(errors))
        return None


def get_ip_location_map(
    error_msg: Callable[[str], None] | None = None,
) -> Any | None:
    """Fetch the IP to location mapping."""
    data = fetch_api_data(IP_LOCATION_API, error_msg=error_msg)
    if data and data.get("status") == "success":
        return data
    if error_msg:
        error_msg(
            f"API error: {data.get('message', 'Unknown error')}"
            if data else "Unknown error"
        )
    return None


def lookup_live_weather(
    latitude: float,
    longitude: float,
    weather_models: str,
    error_msg: Callable[[str], None] | None = None,
) -> Any | None:
    """Get live weather data."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "hourly": (
            "temperature,"
            "windspeed,"
            "precipitation_probability,"
            "uv_index,"
            "snowfall,"
            "cloudcover"
        ),
        "timezone": "auto",
        "model": weather_models,
    }
    data = fetch_api_data(WEATHER_API, params=params, error_msg=error_msg)
    if data:
        return data
    if error_msg:
        error_msg(
            f"API error: Perharps {latitude}, {longitude} location or {weather_models} model is invalid, please try again."
            if data else "Unknown error"
        )
    return None


def retrieve_local_infos(
    city: str | None,
    country: str | None,
    error_msg: Callable[[str], None] | None = None,
) -> Dict[str, str] | None:
    """Retrieve local information based on city and country."""
    if city is None:
        return None
    query = f"{city},{country}" if country else city
    params = {
        "name": query,
        "count": 1,
        "language": "en",
        "format": "json"
    }
    data = fetch_api_data(RETRIEVE_LOCAL, params=params, error_msg=error_msg)

    if data is None:
        if error_msg:
            error_msg(
                f"Cannot find entry for {query}.\n"
                f"Please enter another name for {query} city/country."
            )
        return None

    if "results" in data and len(data["results"]) > 0:
        place = data["results"][0]
        try:
            return {
                "city": place.get("name", ""),
                "country": place.get("country", ""),
                "latitude": place.get("latitude", 0.0),
                "longitude": place.get("longitude", 0.0),
                "timezone": place.get("timezone", "")
            }
        except Exception as error:
            if error_msg:
                error_msg(f"Cannot find {error} for {query}.")
            return None

    if error_msg:
        error_msg(
            f"API error: Perharps {query} is invalid, please try again."
            if data else "Unknown Errors"
        )
    return None


def validate_location_input(
    user_location: str,
    error_msg: Callable[[str], None] | None = None,
) -> bool:
    """Validate the user input for location."""
    if user_location == "":
        if error_msg:
            error_msg("Location input cannot be empty.")
        return False

    if len(user_location.split(", ")) > 2:
        if error_msg:
            error_msg("Format 'City, Country' is not follow?")
        return False

    if len(user_location.split(", ")) == 2:
        city, _ = user_location.split(", ")
        if city == "":
            if error_msg:
                error_msg("Country can be empty but not city.")
            return False

    return True


def get_ip_message(
    city: str,
    country: str,
    longitude: float,
    latitude: float,
    local_time: str,
    timezone: str,
) -> str:
    """General Format to display the IP message."""
    return (
        f"{city}, {country}\n"
        f"{latitude}, {longitude}\n"
        f"{local_time}\n"
        f"{timezone}"
    )


def api_model_for_ui(ui_name: str) -> str:
    """Return API model code for given UI display name."""
    return MODEL_MAP.get(ui_name, "ecmwf_ifs")


def ui_name_for_api(api_code: str) -> str:
    """Return UI display name for given API model code."""
    for ui, code in MODEL_MAP.items():
        if code == api_code:
            return ui
    return "ECMWF IFS"


def model_ui_list() -> list[str]:
    """Return list of UI model names (preserve order of MODEL_MAP keys)."""
    return list(MODEL_MAP.keys())


def validate_feelings(
    current_time: datetime,
    temp: int | float,
    precipitation: int | float,
    windspeed: int | float,
    cloudcover: int | float,
    snowfall: int | float,
    uv_index: int | float,
) -> tuple[str, str]:
    """Cinnamoroll's emotional state based on the weather."""

    emotional_state = ""
    emotional_message = ""

    hour = current_time.hour
    is_daytime = 6 <= hour < 18

    if not is_daytime:
        # At night, UV index is always low
        # No need sunscreen, assume 0
        uv_index = 0

    if precipitation >= 40:
        emotional_state = "Rainy" if is_daytime else "Rainy Night"
        emotional_message = (
            "Oh no, it will get wet ⛈️🌧️.\n"
            "Remember to take an umbrella, wear raincoat and your favorite rainny boot!"
            if is_daytime else
            "Raindrops are singing lullabies outside ⛈️🌧️…\n"
            "Perfect time to cuddle and long nap 💤."
        )

    elif windspeed >= 30:
        emotional_state = "Windy"
        emotional_message = (
            "Wooosh 💨...I'm a windmill on this day with my ears alone!\n"
            "Hold onto your hat (and maybe me too) so we don't blow away 🍃!"
        )

    elif temp >= 30 or uv_index >= 6:
        emotional_state = "Hot" if is_daytime else "Hot Night"
        emotional_message = (
            "Oh noo I have melt into a cinamon bun puddle 🫠🥮.\n"
            "Stay cool with shade, fans, and cold lemonade!"
            if is_daytime else
            "Phew… it's still burningly hot 🌙🔥.\n"
            "Evening watermelon and Moon gazing make the best summer night!"
        )

    elif temp <= 7 or snowfall > 0:
        emotional_state = "Cold"
        emotional_message = (
            "Brrr… I'm turning into a cinnamon ice cube ❄️!\n"
            "Maybe a great condition to a build snowman, tho ☃️🌨️!\n"
            "Keep your body warm with Mulled Wine, fluffy sock, and warm honey Cinnamon Roll."
        )

    elif (
        16 <= temp <= 28
        and precipitation < 20
        and windspeed < 20
        and uv_index <= 5
        and cloudcover < 30
    ):
        emotional_state = "Sunny" if is_daytime else "Clear Night"
        emotional_message = (
            "Yippee! Happy non-depressive time has arrived!.\n"
            "Blue skies, gentle breeze...let's chase clouds on the green lavender field 🪻🌾!\n"
            "Remember to wear sunscreen and sunglasses 🕶️!"
            if is_daytime else
            "The night sky is clear and full of stars 🌗🌌.\n"
            "I wonder what is on the other side of blackhole 🕳️?"
        )

    elif cloudcover >= 30 and precipitation < 20:
        emotional_state = "Cloudy"
        emotional_message = (
            "I'm dreamy on this day. Some clouds are drifting by to say Hello ☁️.\n"
            "Feeling cozy and soft, like a fluffy candy and marshmallow 🍡!"
        )

    elif precipitation < 20 and (7 < temp < 16 or temp > 28):
        emotional_state = "Neutral"
        emotional_message = (
            "Hmm…I feel kinda in-between ☁️.\n"
            "Not too bad, not too great...I want to lie around all day long 🐦‍⬛."
        )

    else:
        emotional_state = "No Idea"
        emotional_message = (
            "My knowledge of weather at your place is like blackhole, it's magic 🕳️."
        )

    return emotional_state, emotional_message


@dataclass
class WeatherData:
    ip_message: str = ""
    weather_message: str = ""

    longitude: float = 0.0
    latitude: float = 0.0
    timezone_name: str = ""
    tz: ZoneInfo | None = None

    input_location: str = ""
    selected_date: str = ""
    weather_models: str = "ecmwf_ifs"

    weather_cache: Dict[str, Any] = None
    cinnamoroll_source: str = ""
    cinnamoroll_message: str = ""

    def use_ip_location(
        self,
        error_msg: Callable[[str], None] | None = None,
    ) -> None:
        """Update the timezone and location automatically.
        
        The live time of user's ip is updated in QML every second.
        """

        get_ip = get_ip_location_map(error_msg)
        if get_ip is None:
            return

        self.longitude = get_ip["lon"]
        self.latitude = get_ip["lat"]

        self.tz = ZoneInfo(get_ip["timezone"])
        current_time = self.get_live_local_time()
        self.timezone_name = str(current_time.tzname())

        self.ip_message = (
            f"{get_ip['city']}, {get_ip['country']}\n"
            f"{self.latitude}, {self.longitude}\n"
            f"{self.selected_date}"
        )

    def use_user_location(
        self,
        error_msg: Callable[[str], None] | None = None
    ) -> None:
        """Use the user's location/timezones to check for weather."""
        if len(self.input_location.split(", ")) == 2:
            city, country = self.input_location.split(", ")
        else:
            city, country = self.input_location, ""
        local_info = retrieve_local_infos(city, country, error_msg)

        if local_info is None:
            return

        get_city = local_info.get("city", "")
        get_country = local_info.get("country", "")
        self.latitude = float(local_info.get("latitude", 0.0))
        self.longitude = float(local_info.get("longitude", 0.0))

        find_timezone = local_info.get("timezone", "")
        if find_timezone != "":
            self.tz = ZoneInfo(local_info["timezone"])
            current_time = self.get_live_local_time()
            self.timezone_name = str(current_time.tzname())
        else:
            self.timezone_name = ""

        self.ip_message = (
            f"{get_city}, {get_country}\n"
            f"{self.latitude}, {self.longitude}\n"
            f"{self.selected_date}"
        )

    def get_weather_by_date(
        self,
        error_msg: Callable[[str], None] | None = None
    ) -> Tuple[Any, List[str], List[str]] | None:
        """Get weather data by date."""
        weather_data = lookup_live_weather(
            self.latitude, self.longitude, self.weather_models, error_msg
        )

        if weather_data is None:
            return None

        hourly_time = weather_data["hourly"]["time"]
        daily_time = weather_data["daily"]["time"]
        return weather_data, daily_time, hourly_time

    def live_weather_data(
        self,
        error_msg: Callable[[str], None] | None = None
    ) -> Dict[str, Any] | None:
        """Pull live weather data from Open-Meteo API."""
        returned_weather = self.get_weather_by_date(error_msg)
        if returned_weather is None:
            return None

        weather, daily_time, hourly_time = returned_weather

        current_time = self.get_live_local_time()
        time_format = current_time.replace(minute=0, second=0, microsecond=0)

        try:
            hourly_idx = hourly_time.index(
                time_format.strftime(f"{self.selected_date}T%H:%M")
            )
            daily_idx = daily_time.index(time_format.strftime(self.selected_date))
        except ValueError:
            if error_msg:
                error_msg(
                    f"{self.selected_date} is not in the time list for {self.input_location}.\n"
                    "Perharps this location has timezone into the future ;)?\n"
                    "Fallback to 'tomorrow'. Please re-select date of tomorrow and refresh to get correct weather data."
                )
            hourly_idx = 0
            daily_idx = 0

        temperature = weather["hourly"]["temperature"][hourly_idx]
        windspeed = weather["hourly"]["windspeed"][hourly_idx]
        precip_prob = weather["hourly"]["precipitation_probability"][hourly_idx]
        cloud_distribution = weather["hourly"]["cloudcover"][hourly_idx]
        snowfall = weather["hourly"]["snowfall"][hourly_idx]
        uv_index = weather["hourly"]["uv_index"][hourly_idx]

        max_temp_of_day = weather["daily"]["temperature_2m_max"][daily_idx]
        min_temp_of_day = weather["daily"]["temperature_2m_min"][daily_idx]

        return {
            "Temperature": temperature,
            "Max Temperature of Day": max_temp_of_day,
            "Min Temperature of Day": min_temp_of_day,
            "Wind Speed": windspeed,
            "Chance of Rain": precip_prob,
            "Cloud Cover": cloud_distribution,
            "Sum snowfall": snowfall, # hourly sum of snowfall in centimeters
            "UV Index": uv_index,
        }

    def auto_weather_update(
        self,
        error_msg: Callable[[str], None] | None = None,
    ) -> Dict[str, int | float] | None:
        """Update the weather data automatically."""
        self.weather_cache = self.live_weather_data(error_msg)

        if self.weather_cache is None:
            if error_msg:
                error_msg("Failed to fetch weather data.")
            return None
        
        day_name = datetime.strptime(self.selected_date, '%Y-%m-%d').strftime('%A')

        self.weather_message = (
            f"Weather on {day_name}, {self.selected_date}\n"
            f"Temperature 🌡️: {self.weather_cache['Temperature']} °C\n"
            f"Min. 🌡️: {self.weather_cache['Min Temperature of Day']} °C\n"
            f"Max. 🌡️: {self.weather_cache['Max Temperature of Day']} °C\n"
            f"Cloud ☁️: {self.weather_cache['Cloud Cover']} %\n"
            f"Precipitation ☔🌧️: {self.weather_cache['Chance of Rain']} %\n"
            f"Wind speed 🍃: {self.weather_cache['Wind Speed']} km/h\n"
            f"Snowfall ☃️❄️: {self.weather_cache['Sum snowfall']} cm\n"
            f"UV Index 🔆: {self.weather_cache['UV Index']}"
        )

    def get_live_local_time(self) -> datetime:
        """Update the live local time of user's location input every 1 second."""
        return datetime.now(self.tz)
    
    def validation_and_live_update(
        self,
        error_msg: Callable[[str], None] | None = None
    ) -> None:
        """Update location + weather depending on input_location."""
        if self.input_location.strip():
            if validate_location_input(self.input_location, error_msg):
                self.use_user_location(error_msg)
            else:
                self.use_ip_location(error_msg)
        else:
            self.use_ip_location(error_msg)

        self.auto_weather_update(error_msg)
        self.cinnamoroll_emotions(error_msg)

    def cinnamoroll_emotions(
        self,
        error_msg: Callable[[str], None] | None = None
    ) -> None:
        """Return cinnamoroll expressions based on weather."""
        if self.weather_cache is None:
            if error_msg:
                error_msg("Failed to fetch weather data.")
            return None

        expression, self.cinnamoroll_message = validate_feelings(
            self.get_live_local_time(),
            self.weather_cache["Temperature"],
            self.weather_cache["Chance of Rain"],
            self.weather_cache["Wind Speed"],
            self.weather_cache["Cloud Cover"],
            self.weather_cache["Sum snowfall"],
            self.weather_cache["UV Index"],
        )
        self.cinnamoroll_source = f"../resources/cinnamoroll/{expression}.png"
