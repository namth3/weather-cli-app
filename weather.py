from configparser import ConfigParser
import argparse
import json
import sys
from urllib import parse, request, error
from pprint import pp
import style

BASE_WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
# Weather Condition Codes
# https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2
THUNDERSTORM = range(200, 300)
DRIZZLE = range(300, 400)
RAIN = range(500, 600)
SNOW = range(600, 700)
ATMOSPHERE = range(700, 800)
CLEAR = range(800, 801)
CLOUDY = range(801, 900)

def _get_api_key():
    """Fetch the API key from your configuration file.

    Expects a configuration file named "secrets.ini" with
    structure
    [openweather] 
    api_key=<YOUR-OPENWEATHER-API-KEY>
    """
    config = ConfigParser()
    config.read("secrets.ini")
    return config["openweather"]["api_key"]


def read_user_cli_args():
    """Handles the CLI user interactions.

    Returns:
    argparse.Namespace: Populated namespace object
    """
    parser = argparse.ArgumentParser(
        description="gets weather and temperature information for a city"
    )
    parser.add_argument(
        "city", nargs="+",type=str, help="enter the city name"
    )
    parser.add_argument(
        "-i",
        "--imperial",
        action="store_true",
        help="display the temperature imperial units",
    )
    return parser.parse_args()

def build_weather_query(city_input, imperial=False):
    """Builds the URL for and API reuquest to OpenWeather API
    Args:
        city_input (List[str]): Name of a city colleted by argparse
        imperial (bool): Whether or not to use imperial unites for temperature

    Returns:
        str: URL formmated for a call to OpenWeather's city name endpoint 
    """
    api_key = _get_api_key()
    city_name = " ".join(city_input)
    url_encoded_city_name = parse.quote_plus(city_name)
    units = "imperial" if imperial else "metric"
    url = (
        f"{BASE_WEATHER_API_URL}?q={url_encoded_city_name}"
        f"&units={units}&appid={api_key}"
    )
    return url

def get_weather_data(query_url):
    """Makes an API request to a URL and return the data as a Python object
    Args:
        query_url(str): URL formmated for OpenWeather's city name endpoint
    Returns:
        dict: weather information for a specific city
    """
    try:
        response = request.urlopen(query_url)
    except error.HTTPError as http_error:
        if http_error == 401: 
            sys.exit("Access denied. Check your API key.")
        elif http_error == 404:
            sys.exit("Can't find weather data for this city.")
        else:
            sys.exit(f"Something went wrong...({http_error.code})")
    data = response.read()
    return json.loads(data)
def _select_weather_display_params(weather_id):
    if weather_id in THUNDERSTORM:
        display_params = ("💥",style.RED)
    elif weather_id in DRIZZLE:
        display_params = ("🌧️",style.CYAN)
    elif weather_id in RAIN:
        display_params = ("💧",style.BLUE)
    elif weather_id in SNOW:
        display_params = ("⛄️",style.WHITE)
    elif weather_id in ATMOSPHERE:
        display_params = ("🌀",style.BLUE)
    elif weather_id in CLEAR:
        display_params = ("🌞",style.YELLOW)
    elif weather_id in CLOUDY:
        display_params = ("🌥️",style.WHITE)
    else:
        display_params = (style.RESET)
    return display_params
def display_weather_info(weather_data, imperial=False):
    """Print formatted weather information about a city.
    Args:
        weather_data (dict): API response from OpenWeather by city name
        imperial (bool): Whether or not to user imperial units for temperature
    More information at OpenWeather
    """
    city = weather_data['name']
    weather_id = weather_data["weather"][0]['id']
    weather_description = weather_data['weather'][0]['description']
    temperature = weather_data['main']['temp']
    
    style.change_color(style.REVERSE)
    print(f"{city:^{style.PADDING}}",end="")
    style.change_color(style.RESET)

    weather_symbol, color = _select_weather_display_params(weather_id)
    style.change_color(color)
    print(f"\t{weather_symbol} {weather_description.capitalize():^{style.PADDING}}", end=" ")
    style.change_color(style.RESET)
    
    print(f"({temperature}°{'F' if imperial else 'C'})")

if __name__ == "__main__":
    user_args = read_user_cli_args()
    # print(user_args.city, user_args.imperial)
    query_url = build_weather_query(user_args.city,user_args.imperial)
    # print(query_url)
    weather_data = get_weather_data(query_url)
    # pp(weather_data)
    display_weather_info(weather_data,user_args.imperial)
   



