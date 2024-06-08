#!/usr/bin/env python3

import requests
from pprint import pprint


class Weather:
    """
    This module provides a Weather class that interacts with OpenWeatherMap API.
    It fetches and processes weather data for a given location.

    Attributes:
    -----------
        api_key (str): The API key from OpenWeatherMap.
        latitude (float): Latitude of the location to fetch weather data for.
        longitude (float): Longitude of the location to fetch weather data for.

    Properties:
    -----------
        data (dict): Fetches weather data from OpenWeatherMap API and stores it.
        max_temperature (int): The maximum temperature in Celsius.
        humidity (int): The relative humidity as a percentage.
        pressure (int): The atmospheric pressure in hectopascals.
        wind_speed (float): The speed of the wind in meters per second.
        visibility (int): The visibility in kilometers.
        sunset (int): The time of sunset in seconds since the Unix epoch.
        sunrise (int): The time of sunrise in seconds since the Unix epoch.
        location (str): The name of the location.
        wind_deg (int): The direction of the wind in degrees.

    Methods:
    --------
        kelvin2celsius(float) -> float: Converts temperature from Kelvin to Celsius.
        __str__() -> str: Returns a string representation of the weather data for the location.
    """

    def __init__(
        self,
        api_key="6eb1659474bdf84f068aba3fbfe37ce6",
        latitude=49.0521162,
        longitude=-122.329479,
    ):
        """
        Initializes a Weather object.

        Args:
        ------
            api_key (str): The API key from OpenWeatherMap.
            latitude (float): Latitude of the location to fetch weather data for.
            longitude (float): Longitude of the location to fetch weather data for.
        """
        self.api_key = api_key
        self.latitude = latitude
        self.longitude = longitude

    @property
    def data(self):
        """
        Fetches and processes weather data from OpenWeatherMap API.

        If no data is available, it will fetch the data. Otherwise, it will return the stored data.

        Returns:
        --------
            dict: Weather data for the location.
        """
        if not hasattr(self, "_data"):
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={self.latitude}&lon={self.longitude}&appid={self.api_key}"
            self._data = requests.get(url).json()
        return self._data

    @property
    def max_temperature(self):
        """
        Returns the maximum temperature in Celsius.

        This is achieved by calling the kelvin2celsius method on the current max temperature.

        Returns:
        --------
            int: The maximum temperature in Celsius.
        """
        return self.kelvin2celsius(self.data["main"]["temp_max"])

    @property
    def humidity(self):
        """
        Returns the relative humidity as a percentage.

        This is fetched directly from OpenWeatherMap API data.

        Returns:
        -------
            int: The relative humidity as a percentage.
        """
        return self.data["main"]["humidity"]

    @property
    def pressure(self):
        """
        Returns the atmospheric pressure in hectopascals.

        This is fetched directly from OpenWeatherMap API data.

        Returns:
        --------
            int: The atmospheric pressure in hectopascals.
        """
        return self.data["main"]["pressure"]

    @property
    def wind_speed(self):
        """
        Returns the speed of the wind in meters per second.

        This is fetched directly from OpenWeatherMap API data.

        Returns:
        ---------
            float: The speed of the wind in meters per second.
        """
        return self.data["wind"]["speed"]

    @property
    def visibility(self):
        """
        Returns the visibility in kilometers.

        This is fetched directly from OpenWeatherMap API data.

        Returns:
        ---------
            int: The visibility in kilometers.
        """
        return self.data["sys"]["visibility"]

    @property
    def sunset(self):
        """
        Returns the time of sunset in seconds since the Unix epoch.

        This is fetched directly from OpenWeatherMap API data.

        Returns:
        --------
            int: The time of sunset in seconds since the Unix epoch.
        """
        return f"Current Temperature in {self.location}: {self.kelvin2celsius(self.max_temperature)}°C\nDescription: {self.data['weather'][0]['description'].capitalize()}"


if __name__ == "__main__":
    Abbotsford = Weather()
    print(Abbotsford.data)
