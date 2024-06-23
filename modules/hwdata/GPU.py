#!/usr/bin/env python3

import subprocess
import re
from ExecutionTimer import ExecutionTimer


class GpuData:
    """
    A class for querying GPU data using nvidia-smi tool.

    Attributes:
    ----------
        type (str): Type of the device, always 'GPU'.
        name (str): Name of the GPU.

    Properties:
    -----------
        temp : str
            Current temperature of the GPU core.
        core_temp : str
            Current temperature of the GPU core.
        memory_temp : str
            Current temperature of the GPU memory.
        core_clock : str
            Current graphics clock speed of the GPU in MHz.
        max_core_clock : str
            Maximum graphics clock speed of the GPU in MHz.
        memory_clock : str
            Current memory clock speed of the GPU in MHz.
        max_memory_clock : str
            Maximum memory clock speed of the GPU in MHz.
        memory_usage : str
            Current utilization of the GPU memory as a percentage.
        voltage : float
            Voltage of the GPU in volts.
        power : int
            Current power draw of the GPU in Watts.
        core_usage : str
            Current utilization of the GPU cores as a percentage.
        timestamp : str
            The time when nvidia-smi was last run.

    Methods:
        gpu_name(short=False) -> str:
            Return the name of the GPU. If short is True, return only model number.

    """

    def __init__(self):
        self.type = "GPU"
        self.name = self.gpu_name(short=True)

    @property
    def temp(self):
        """
        Get current temperature of the GPU core.

        Returns:
        -----------

            str: Current temperature of the GPU core in Celsius.
        """
        return self.core_temp

    @property
    def core_temp(self):
        """
        Get current temperature of the GPU core.

        Returns:
        -----------

            str: Current temperature of the GPU core in Celsius.
        """
        # temperature.gpu
        core_temp = subprocess.run(
            "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader",
            shell=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return core_temp

    @property
    def memory_temp(self):
        """
        Get current temperature of the GPU memory.

        Returns:
        -----------

            str: Current temperature of the GPU memory in Celsius.
        """
        # temperature.memory
        memory_temp = subprocess.run(
            "nvidia-smi --query-gpu=temperature.memory --format=csv,noheader",
            shell=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return memory_temp

    @property
    def core_clock(self):
        """
        Get current graphics clock speed of the GPU in MHz.

        Returns:
        -----------

            str: Current graphics clock speed of the GPU in MHz.
        """
        # clocks.current.graphics
        core_clock = (
            subprocess.run(
                "nvidia-smi  --query-gpu=clocks.current.graphics  --format=csv,noheader",
                shell=True,
                capture_output=True,
                text=True,
            )
            .stdout.replace("MHz", "")
            .strip()
        )
        return core_clock

    @property
    def max_core_clock(self):
        """
        Get maximum graphics clock speed of the GPU in MHz.

        Returns:
        -----------

            str: Maximum graphics clock speed of the GPU in MHz.
        """
        # clocks.max.graphics
        max_core_clock = (
            subprocess.run(
                "nvidia-smi  --query-gpu=clocks.max.graphics  --format=csv,noheader",
                shell=True,
                capture_output=True,
                text=True,
            )
            .stdout.replace("MHz", "")
            .strip()
        )
        return max_core_clock

    @property
    def memory_clock(self):
        """
        Get current memory clock speed of the GPU in MHz.

        Returns:
        -----------

            str: Current memory clock speed of the GPU in MHz.
        """
        # clocks.current.memory
        memory_clock = (
            subprocess.run(
                "nvidia-smi  --query-gpu=clocks.current.memory  --format=csv,noheader",
                shell=True,
                capture_output=True,
                text=True,
            )
            .stdout.replace("MHz", "")
            .strip()
        )
        return memory_clock

    @property
    def max_memory_clock(self):
        """
        Get maximum memory clock speed of the GPU in MHz.

        Returns:
        -----------

            str: Maximum memory clock speed of the GPU in MHz.
        """
        # clocks.max.memory
        max_memory_clock = (
            subprocess.run(
                "nvidia-smi  --query-gpu=clocks.max.memory  --format=csv,noheader",
                shell=True,
                capture_output=True,
                text=True,
            )
            .stdout.replace("MHz", "")
            .strip()
        )
        return max_memory_clock

    @property
    def memory_usage(self):
        """
        Get current utilization of the GPU memory as a percentage.

        Returns:
        -----------

            str: Current utilization of the GPU memory as a percentage.
        """
        memory_usage = (
            subprocess.run(
                "nvidia-smi  --query-gpu=utilization.memory  --format=csv,noheader",
                shell=True,
                capture_output=True,
                text=True,
            )
            .stdout.replace("%", "")
            .strip()
        )
        return memory_usage

    @property
    def voltage(self):
        """
        Get the voltage of the GPU in volts.

        Returns:
        -----------

            float: Voltage of the GPU in volts.
        """
        voltage_regex = re.compile(r"(\d+.\d+)")
        voltage_subprocess = subprocess.run(
            'nvidia-smi  -q  --display=Voltage  |  grep -o -P "Graphics.*"',
            shell=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        matches = "  ".join(voltage_regex.findall(voltage_subprocess))
        volts = round(float(matches) / 1000, 2)
        return float(volts)

    @property
    def power(self):
        """
        Get the current power draw of the GPU in watts.

        Returns:
        -----------

            str: Current power draw of the GPU in Watts.
        """
        # power.draw
        power = (
            subprocess.run(
                "nvidia-smi  --query-gpu=power.draw  --format=csv,noheader",
                shell=True,
                capture_output=True,
                text=True,
            )
            .stdout.replace("W", "")
            .strip()
        )
        return round(float(power))

    @property
    def core_usage(self):
        """
        Get the current GPU utilization as a percentage.

        Returns:
        -----------

            str: Current GPU utilization in percentage.
        """
        core_usage = (
            subprocess.run(
                "nvidia-smi  --query-gpu=utilization.gpu  --format=csv,noheader",
                shell=True,
                capture_output=True,
                text=True,
            )
            .stdout.replace("%", "")
            .strip()
        )
        return core_usage

    def gpu_name(self, short=False):
        """
        Get the name of GPU.

        Returns:
        -----------

            str : Name of GPU with optional argument to get short model name (last part)
        """
        name_regex = re.compile(
            r"(AMD|NVIDIA|Intel)\s?(\s?GeForce\s?|\s?Radeon\s?)\s?(\sGTX\s?|\s?RTX\s?)(.*)"
        )
        subout = subprocess.run(
            "nvidia-smi  --query-gpu=name  --format=csv,noheader",
            shell=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        matches = name_regex.findall(subout)
        if short:
            self.name = matches[0][-1]
        else:
            self.name = "  ".join(matches[0])
        return self.name

    @property
    def timestamp(self):
        """
        Current timestamp

        Returns:
        -----------

            str : GPU timestamp in milliseconds since boot
        """
        timestamp = subprocess.run(
            "nvidia-smi  --query-gpu=timestamp  --format=csv,noheader",
            shell=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return timestamp

    @property
    def fan_speed(self):
        """
        Get the fan speed as a percentage of its maximum RPM rate.

        Returns:
        -----------
             str   : Fan speed in percentage
        """
        fan_speed = subprocess.run(
            "nvidia-smi --query-gpu=fan.speed --format=csv,noheader",
            shell=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return fan_speed.replace("%", "").strip()

    def csv(self, header=False, timestamp=False, units=False):
        """
        Returns the object properties as a CSV string.

        Paramaters:
        ---------
            header (bool) : If True, include a header in the CSV output
            timestamp (bool) : If True, include the timestamp in the CSV output. Defaults to True.

        Returns:
        --------
            csv (str): CSV string of object properties
        """
        DATETIME_REGEX = re.compile(r"\d+(-|/)\d+(-|/)\d+\s\d+:\d+:\d+(\.\d+)?")
        header_ = ""

        unit_definitions = [" °C", " V", " MHz", " %", " W", " MHz", " %"]
        template = f"{self.temp},{self.voltage},{self.core_clock},{self.core_usage},{self.power},{self.memory_clock},{self.memory_usage}"

        if timestamp:
            template = f"{self.timestamp},{template}"
        if header:
            if timestamp:
                keys = [
                    "Time",
                    "Temp",
                    "Voltage",
                    "Core Clock",
                    "Core Usage",
                    "Power",
                    "Memory Clock",
                    "Memory Usage",
                ]
            else:
                keys = [
                    "Temp",
                    "Voltage",
                    "Core Clock",
                    "Core Usage",
                    "Power",
                    "Memory Clock",
                    "Memory Usage",
                ]
            header_ = ",".join(keys)
            template = header_ + "\n" + template
        # Append units to the end of each field
        if units:
            # The offset is used to account for the fact that we are adding units after each field
            # rather than at the end of each field. Time allows us to skip the timestamp field when adding units.
            offset = 0
            # Ignore header when adding units
            if header_:
                values = template.replace(header_, "").lstrip().split(",")
            else:
                values = template.lstrip().split(",")
            for i, value in enumerate(values):
                try:
                    if not DATETIME_REGEX.match(value):
                        values[i] = f"{value}{unit_definitions[i-offset]}"
                    else:
                        # Dont assign a unit to the timestamp, so we subtract one from the unit index.
                        offset = 1
                except IndexError as e:
                    pass
            # Join back together with commas and add the header back in.
            template = f'{header_}\n{", ".join(values)}' if header else ", ".join(values)
        # Format the template with the data from this instance of the class
        formatted = template.format(
            temp=self.temp,
            voltage=self.voltage,
            core_clock=self.core_clock,
            core_usage=self.core_usage,
            power=self.power,
            memory_clock=self.memory_clock,
            memory_usage=self.memory_usage,
        )
        return formatted

    def __str__(self):
        """
        Return string representation of GPU object.

        Returns:
        -----------
             str   : String representation of GPU object.
        """
        return (
            f"GPU: {self.name}\n"
            f"Core Temp: {self.core_temp} °C\n"
            f"Core Clock: {self.core_clock} MHz\n"
            f"Memory Clock: {self.memory_clock} MHz\n"
            f"Memory Usage: {self.memory_usage}    %\n"
            f"Core Usage: {self.core_usage}    %\n"
            f"Power: {self.power} W\n"
            f"Voltage: {self.voltage} V\n"
            f"Fan fan_speed {self.fan_speed}%\n"  # Added this line
        ).strip()

    def __call__(self):
        """
        Return dictionary representation of GPU object.

        Returns:
        -----------
            dict : Dictionary representation of GPU object.
        """
        return self.__dict__

    def __repr__(self):
        """Return Class representation."""
        return f"{self.__class__.__name__}({self.__dict__})"


# Example
if __name__ == "__main__":
    gpu = GpuData()
    print(f"Full GPU Name: {gpu.gpu_name()}")
    print(f"Short GPU Name: {gpu.gpu_name(short=True)}")
    print(str(gpu))
    print("\nBASIC")
    print(gpu.csv())
    print("\nHEADER")
    print(gpu.csv(header=True))
    print("\nHEADER, TIMESTAMP")
    print(gpu.csv(header=True, timestamp=True))
    print("\nUNITS")
    print(gpu.csv(header=False, timestamp=False, units=True))
    print("\nALL")
    print(gpu.csv(header=True, timestamp=True, units=True))
