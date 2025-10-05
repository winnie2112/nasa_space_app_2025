def get_descriptions(rain, temperature, snowfall=None, wind_speed=None, cloud_cover=None):
    # in mm
    if rain == None:
        rain_description = None
    elif rain < 1:
        rain_description = "No Rain"
    elif rain >= 1 and rain < 30:
        rain_description = "Rainy"
    else:
        rain_description = "Heavy Rain"

    # in cm
    if snowfall == None:
        snow_description = None
    elif snowfall < 1:
        snow_description = "No Snow"
    elif snowfall >= 1 and snowfall < 20:
        snow_description = "Snowy"
    else:
        snow_description = "Heavy Snow"
    
    # in km/h
    if wind_speed == None:
        wind_description = None
    elif wind_speed < 1:
        wind_description = "No Wind"
    elif wind_speed >= 1 and wind_speed <= 20:
        wind_description = "Gentle Breeze"
    elif wind_speed > 20 and wind_speed < 30:
        wind_description = "Windy"
    else:
        wind_description = "Very Windy"

    # in °C
    if temperature == None:
        temperature_description = None
    elif temperature <= 0:
        temperature_description = "Very Cold"
    elif temperature > 0 and temperature <= 10:
        temperature_description = "Cold"
    elif temperature > 10 and temperature <= 20:
        temperature_description = "Mild"
    elif temperature > 20 and temperature < 30:
        temperature_description = "Warm"
    else:
        temperature_description = "Very Hot"

    # in %
    if cloud_cover == None:
        cloud_description = None
    elif cloud_cover <= 30:
        cloud_description = "Clear"
    elif cloud_cover > 30 and cloud_cover <= 70:
        cloud_description = "Partly Cloudy"
    elif cloud_cover > 70 and cloud_cover < 100:
        cloud_description = "Cloudy"
    else:
        cloud_description = "Overcast"
    
    return rain_description, temperature_description,  snow_description, wind_description, cloud_description