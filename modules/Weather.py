#!/usr/bin/env python3

import requests
from pprint import pprint


class Weather:
    def __init__(self, api_key="6eb1659474bdf84f068aba3fbfe37ce6", latitude=49.0521162, longitude=-122.329479):
        """
        Initializes the Weather object with data from the OpenWeatherMap API response.

        Args:
            json_response (dict): The JSON response from the OpenWeatherMap API.
        """
        self.api_key = api_key
        self.latitude = latitude
        self.longitude = longitude

        self.data = self.update()
        
        # self.temperature_ = self.kelvin2celsius(self.data["main"]["temp"])
        # self.min_temperature_ = self.kelvin2celsius(self.data["main"]["temp_min"])
        # self.max_temperature_ = self.kelvin2celsius(self.data["main"]["temp_max"])
        # self.description_ = self.data["weather"][0]["description"]
        # self.description_icon = self.data["weather"][0]["icon"]
        # self.humidity_ = self.data["main"]["humidity"]
        # self.pressure_ = self.data["main"]["pressure"]
        # self.wind_speed_ = self.data["wind"]["speed"]
        # self.wind_deg_ = self.data["wind"]["deg"]
        # self.visibility_ = self.data["visibility"]
        # self.sunset_ = self.data["sys"]["sunset"]
        # self.sunrise_ = self.data["sys"]["sunrise"]
        # self.location_ = self.data["name"]
        # self.country_ = self.data["sys"]["country"]
        # self.id = self.data["weather"][0]["id"]

        # self.temperature_ = self.data.get("sys").get("temp")
        # self.min_temperature_ = self.min_temperature
        # self.max_temperature_ = self.max_temperature
        # self.humidity_ = self.humidity
        # self.pressure_ = self.pressure
        # self.wind_speed_ = self.wind_speed
        # self.visibility_ = self.visibility
        # self.sunset_ = self.sunset
        # self.sunrise_ = self.sunrise
        # self.description_ = self.description
        # self.location_ = self.location
        # self.sunrise_ = self.sunrise
        # self.sunset_ = self.sunset
        # self.wind_deg_ = self.wind_deg
        # self.wind_direction_ = self.wind_direction
    
    @property
    def temperature(self):
        self.data = self.update()
        self.temperature_ = self.kelvin2celsius(self.data["main"]["temp"])
        return  self.temperature_
    @property
    def min_temperature(self):
        self.min_temperature_ = self.update().get("sys").get("temp_min")
        return  self.min_temperature_
    @property
    def max_temperature(self):
        self.max_temperature_ = self.update().get("sys").get("temp_max")
        return  self.max_temperature_
    @property
    def humidity(self):
        self.humidity_ = self.update().get("sys").get("humidity")
        return  self.humidity_
    @property
    def pressure(self):
        self.pressure_ = self.update().get("sys").get("pressure")
        return  self.pressure_
    @property
    def wind_speed(self):
        self.wind_speed_ = self.update().get("sys").get("speed")
        return  self.wind_speed_
    @property
    def visibility(self):
        self.visibility_ = self.update().get("sys").get("visibility")
        return  self.visibility_
    @property
    def sunset(self):
        self.sunset_ = self.update().get("sys").get("sunset")
        return  self.sunset_
    @property
    def sunrise(self):
        self.sunrise_ = self.update().get("sys").get("sunrise")
        return self.sunrise_
    
    def kelvin2celsius(self, kelvin):
        """
        Converts temperature from Kelvin to Celsius.

        Args:
            kelvin (float): Temperature in Kelvin.

        Returns:
            float: Temperature in Celsius.
        """
        return round(kelvin - 273.15, 2)


    @property
    def location(self):
        self.location_ = self.update().get("name")
        return self.location_

    @property
    def wind_deg(self):
        self.wind_deg_ = self.update().get("wind").get("deg")
        return self.wind_deg_

    def update(self):
        # Build the URL
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={self.latitude}&lon={self.longitude}&appid=6eb1659474bdf84f068aba3fbfe37ce6"
        # Make the API request
        response = requests.get(url)
        return response.json()

    def __call__(self, latitude, longitude):
        self.update(latitude, longitude)

    def __int__(self):
        return int(self.kelvin2celsius(self.temperature))

    def __str__(self):
        """
        Returns a string representation of the weather data for the location.

        Returns:
            str: A formatted string with the current temperature and description.
        """
        return f"Current Temperature in {self.location}: {self.temperature}°C\nDescription: {self.description.capitalize()}"

if __name__ == "__main__":
    #MapleRidge = Weather()
    #pprint(Weather(49.2193, -122.6010))
    Abbotsford = Weather()
    print(Abbotsford.update())