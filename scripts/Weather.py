#!/usr/bin/env python3

import requests
from pprint import pprint


class Weather:
    def __init__(self, json_response):
        """
        Initializes the Weather object with data from the OpenWeatherMap API response.

        Args:
            json_response (dict): The JSON response from the OpenWeatherMap API.
        """
        self.data = json_response
        self.temperature = self.kelvin2celsius(self.data["main"]["temp"])
        self.min_temperature = self.kelvin2celsius(self.data["main"]["temp_min"])
        self.max_temperature = self.kelvin2celsius(self.data["main"]["temp_max"])
        self.description = self.data["weather"][0]["description"]
        self.humidity = self.data["main"]["humidity"]
        self.pressure = self.data["main"]["pressure"]
        self.wind_speed = self.data["wind"]["speed"]
        self.visibility = self.data["visibility"]
        self.sunset = self.data["sys"]["sunset"]
        self.sunrise = self.data["sys"]["sunrise"]
        self.location = self.data["name"]

    def __str__(self):
        """
        Returns a string representation of the weather data for the location.

        Returns:
            str: A formatted string with the current temperature and description.
        """
        return f"Current Temperature in {self.location}: {self.temperature}°C\nDescription: {self.description.capitalize()}"
    
    def kelvin2celsius(self, kelvin):
        """
        Converts temperature from Kelvin to Celsius.

        Args:
            kelvin (float): Temperature in Kelvin.

        Returns:
            float: Temperature in Celsius.
        """
        return round(kelvin - 273.15, 2)

    def tostring(self, value):
        """
        Converts the value to a string representation using the weather icon index.

        Args:
            value (any): The value to be converted to a string.

        Returns:
            str: The string representation of the value with the weather icon index.
        """
        index = self.data["weather"][0]["icon"]
        return f"{value}"



def get_weather(api_key="6eb1659474bdf84f068aba3fbfe37ce6", latitude=49.0401, longitude=-122.2210):
    """

    Args:
        api_key (str): API key for accessing the OpenWeatherMap API.
        latitude (float): Latitude coordinate for the location.
        longitude (float): Longitude coordinate for the location.

    Returns:
        Weather: Weather object containing the weather data.
    """
    # Build the URL
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}"

    # Make the API request
    response = requests.get(url)
    WeatherObject = Weather(response.json())
    return WeatherObject


if __name__ == "__main__":
    MapleRidge = get_weather()
    print(MapleRidge)
    print(MapleRidge.tostring(MapleRidge.temperature))
    print(MapleRidge.tostring(MapleRidge.description))