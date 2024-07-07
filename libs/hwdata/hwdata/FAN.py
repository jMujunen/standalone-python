#!/usr/bin/env python3

import subprocess
import re
from typing import List, Tuple
from dataclasses import dataclass

# TODO:
# * Add support for renaming xfans (fan1 becomes CPU fan)


@dataclass
class Fan:
    """Class representing a single fan.

    Attributes:
    ----------
        name (str): The name of the fan
        fan_id (str): The id of the fan in lm-sensors output

    Methods:
    --------
        speed() -> int: The current speed of the fan in RPMs.
        query_fans() -> str: The raw output of lm-sensors for this fan.
    """

    def __init__(self, fan_id: str, friendly_name: str | None = None):
        """
        Initialize the fan object with the given fan number.

        Parameters:
        -----------
            fan_id (str): The name representing the fan in lm-sensors
                          For example: Fan('fan1') represents fan1 in

            friendly_name (str): The friendly name of the fan
                                 For example : Fan('fan1', 'CPU') represents
                                 fan1 in lm-sensors

            fan1:            537 RPM  (min =    0 RPM)
            fan2:            592 RPM  (min =    0 RPM)
            fan3:            576 RPM  (min =    0 RPM)
            fan4:            566 RPM  (min =    0 RPM)
            fan5:            580 RPM  (min =    0 RPM)
            fan6:            579 RPM  (min =    0 RPM)
            fan7:              0 RPM  (min =    0 RPM)
            fan8:              0 RPM  (min =    0 RPM)
            fan9:              0 RPM  (min =    0 RPM)
            fan10:             0 RPM  (min =    0 RPM)
            cpu:               0 RPM  (min =    0 RPM)



        """

        if not friendly_name:
            self.name = fan_id
        else:
            self.name = friendly_name
        self.fan_id = fan_id

        self.fan_data_regex = r"^(fan\d+).*([0-9]{3,4})"
        # self.name = self.name

    @property
    def type(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    def query_fans(self) -> dict:
        """
        Query the fan speed data from the sensors and return the fan data in a dictionary format.

        Parameters:
            None

        Returns:
            fan_data (dict): A dictionary containing the fan speed data
        """
        # Get the fan speed data from the sensors using a subprocess
        command_output = subprocess.run(
            f"sensors | grep {self.fan_id}", shell=True, capture_output=True, text=True
        ).stdout.strip()

        # Find all matches in the text {'fan1': '555', 'fan2': '1025'}
        matches = re.findall(self.fan_data_regex, command_output, re.MULTILINE)

        # Process the matches into dictionary format
        speed = matches[0][1]
        name = matches[0][0]
        return speed
        """
        # Return the dictionary if non-empty
        if fan_data:
            speed = fan_data[self.fan_name]
            return speed

        # If no fan speed is matched, return a default or error value
        print("Error: Fan speeds are all 0")
        return "Error: Fan speeds are all 0"
        """

    @property
    def speed(self) -> int:
        return int(self.query_fans()[0]) or 0

    def __str__(self) -> str:
        return f"{self.name}: {self.speed} RPM"


# Example usage
if __name__ == "__main__":
    fans = [
        Fan("fan1", "CPU"),
        Fan("fan2", "REAR"),
        Fan("fan3", "SYS1"),
        Fan("fan4", "SYS2"),
        Fan("fan5", "SYS3"),
        Fan("fan6", "BOTTOM"),
    ]

    for fan in fans:
        print(fan)
        print(fan.speed)

    """
    print(fan1)
    print(int(fan6))
    """
    # print(fans)
    # print(f'Current fan speed: {fans}')  # Output: Current fan speed: `FANSPEED` [555 RPM]
