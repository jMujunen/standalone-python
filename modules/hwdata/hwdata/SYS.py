import subprocess
import re
import psutil
from dataclasses import dataclass


@dataclass()
class Temp:
    """Class for handling temperature sensor data."""

    def __init__(self):
        """Initialize the temperature sensor data."""
        self.type = "SYS"
        # Precompile the regex pattern to match two consecutive digits which represent the temperature
        self.temp_regex = re.compile(r"(\d{2})")
        self.name = "Sys"

    @property
    def temp(self):
        """Get the temperature data from the sensors using a subprocess"""

        command_output = subprocess.run(
            "sensors | grep 'Sensor 2' | awk  '{print $3}'",
            shell=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        # Extract the first matching temperature value
        temperature_match = self.temp_regex.search(command_output)
        if temperature_match:
            return int(temperature_match.group())

        # If no temperature is matched, return a default or error value
        return "Error: Temperature not found"

    def __str__(self):
        """Returns a string representation of the temperature data."""
        current_temp = self.temp
        return f"{current_temp}°C"

    def __int__(self):
        """Return current temperature as int"""
        current_temp = self.temp
        return int(current_temp) if int(current_temp) else 0


@dataclass()
class RAM:
    def __init__(self):
        return None

    def info(self) -> dict:
        return psutil.virtual_memory()

    @property
    def percent_used(self) -> int:
        return int(psutil.virtual_memory().percent)

    def __str__(self) -> str:
        return f"RAM: {self.percent_used}%"


@dataclass()
class Misc:
    def __init__(self):
        return None

    def get_uptime(self):
        # Get the uptime data from the sensors using a subprocess
        command_output = subprocess.run(
            "uptime -p", shell=True, capture_output=True, text=True
        ).stdout.strip()

        # Extract the first matching uptime value
        uptime_match = re.search(r"(\d+\s+\w+.*)+", command_output)
        if uptime_match:
            return uptime_match.group()

        # If no uptime is matched, return a default or error value
        return "Error: Uptime not found"

    def users(self):
        users = psutil.users()
        names = []
        terminals = []
        for user in users:
            names.append(user.name)
            terminals.append(user.terminal)
        return list(zip(names, terminals))


# Example usage
if __name__ == "__main__":
    temp = Temp()
    # Output: Current temperature: `TEMP` [25.0°C]
    print(str(temp))
    print(int(temp))
    print("\n\n")
    print(Misc().get_uptime())
    print(Misc().users())
    print("\n\n")
    print(RAM())
