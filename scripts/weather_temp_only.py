import Weather

WeatherObject = Weather.get_weather()
print(f'{WeatherObject.tostring(WeatherObject.temperature)}°C')
