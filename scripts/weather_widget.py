import Weather

WeatherObject = Weather.get_weather()
print(f'{WeatherObject.description} {WeatherObject.tostring(WeatherObject.temperature)}°C')