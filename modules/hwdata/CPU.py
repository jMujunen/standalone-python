#!/usr/bin/env python3

# TODO:
# *  - [x] Add suppport for specifying which CPU to query

import subprocess
import re
import datetime


class CpuData:
    def __init__(self):
        """
        Initializes an instance of `CpuData`.
        The object contains information about the CPU, including its clock speed, voltage, temperature and name.

        Returns
        ------
            CpuData: An instance of a class containing data about the CPU.
        """
        self.type = 'CPU'
        # Regex patterns for parsing output from 'lscpu' and 'sensors' commands
        # Regex patterns for parsing output from
        # 'lscpu' and 'sensors' commands
        self.clock_speed_regex = re.compile(r'(cpu MHz)\s+:\s+([\d.]+)')
        self.cpu_voltage_regex = re.compile(r'([^+]\d{1,3}\.\d{2,})')
        self.cpu_temp_regex = re.compile(r'(Core \d+).*(\d\d\.\d).*\(high.*\)')
        self.name_regex = re.compile(r'Model name:\s+(.*)')

        # Initialization of properties for CPU data
        self.name = self.cpu_name(short=True)
        self.temp = self.average_temp

    def query_cpu_clocks(self):
        """
        Queries the clock speeds of all cores and returns them in a dictionary.
        The keys are core numbers starting from 1 and the values are their corresponding clock frequencies.

        Returns
        ------
            dict: A dictionary where keys are core numbers (ints) and values are clock frequencies (floats).
        """
        clock_dict = {}
        with open('/proc/cpuinfo', 'r', encoding='utf-8') as f:
            raw_output = f.read()
        if 
        matches = re.findall(self.clock_speed_regex, raw_output)
        count = 1
        for match in matches:
            clock_dict[count] = match[1]
            count += 1

        return clock_dict

    def query_cpu_temp(self):
        """
        Queries the temperature of all cores and returns them in a dictionary.
        The keys are core numbers starting from 1 and the values are their corresponding temperatures.

        Returns
        ------
            dict: A dictionary where keys are core numbers (ints) and values are temperatures (floats).
        """
        temp_dict = {}
        cpu_temperatures = subprocess.run(
            'sensors | grep Core', shell=True, capture_output=True, text=True
        ).stdout.strip()

        matches = re.findall(self.cpu_temp_regex, cpu_temperatures)
        count = 1
        for match in matches:
            temp_dict[count] = match[1]
            count += 1
        return temp_dict

    @property
    def voltage(self):
        """
        Queries the voltage of the CPU and returns it.
        The voltage is rounded to three decimal places.
        """
        cpu_voltage_subproccess = subprocess.run(
            ['echo $(sensors | grep VIN3)'], shell=True, stdout=subprocess.PIPE
        ).stdout.decode("utf-8")
        raw_value = self.cpu_voltage_regex.search(cpu_voltage_subproccess).group(1)
        cpu_voltage = raw_value.strip()
        if len(cpu_voltage) == 4:
            return round(float(cpu_voltage.strip()), 3)
        elif len(cpu_voltage) == 6:
            return round((float(cpu_voltage) / 1000), 3)
        else:
            raise Exception("Error: Voltage not found (requires a 4 or 6 digit number eg 1.25v or 600.00mV)")

    def cpu_clocks_list(self):
        """
        Queries the clock speeds of all cores and returns them in a list.
        The elements are core numbers starting from 1 and their corresponding clock frequencies.

        Returns
        ------
            List[float]: A list where each element is a core number (int) and its corresponding clock frequency (float).
        """
        self.query_clocks = self.query_cpu_clocks()
        return [round(float(clock)) for clock in self.query_clocks.values()]

    def cpu_temp_list(self):
        """
        Queries the temperature of all cores and returns them in a list.
        The elements are core numbers starting from 1 and their corresponding temperatures.

        Returns
        ------
            List[float]: A list where each element is a core number (int) and its corresponding temperature (float).
        """
        self.query_temp = self.query_cpu_temp()
        return [round(float(temp)) for temp in self.query_temp.values()]

    @property
    def average_temp(self):
        """
        Calculates and returns the average CPU temperature as a floating-point number, rounded to three decimal places.

        Returns
        ------
            float: The average CPU temperature in degrees Celsius (float).
        """
        return round(sum(self.cpu_temp_list()) / len(self.cpu_temp_list()))

    @property
    def max_temp(self):
        """
        Returns the maximum CPU temperature as a floating-point number found in all cores.

        Returns
        ------
            float: The maximum CPU temperature in degrees Celsius (float).
        """
        return max(self.cpu_temp_list())

    @property
    def max_clock(self):
        """
        Calculates and returns the highest clock speed among all CPU cores, as a floating-point number.

        Returns
        ------
            float: The maximum clock speed (float).
        """
        return max(self.cpu_clocks_list())

    @property
    def average_clock(self):
        """
        Calculates and returns the average clock frequency of all CPU cores, rounded to three decimal places.

        Returns
        ------
            float: The average clock frequency (float).
        """
        return round(sum(self.cpu_clocks_list()) / len(self.cpu_clocks_list()))

    def cpu_name(self, short=False):
        output = subprocess.run('lscpu | grep "Model name"', shell=True, capture_output=True, text=True)
        stderr = output.stderr.strip()
        stdout = output.stdout.strip()

        if stderr:
            raise Exception(stderr)
            return 1

        matches = re.findall(self.name_regex, stdout)
        for match in matches:
            full_name = match
            short_name = match.split(' ')[-1]
        if short:
            return short_name
        return full_name

    def csv(self, header=False, units=False, timestamp=False):
        """
        Generates a CSV string representation of the current CPU status. The result can include an optional header row, units in the output and/or timestamps.

        Args
        ------
            header (bool, optional): If True, includes a header line at the beginning of the returned CSV string. Defaults to False.
            units (bool, optional): If True, appends the units (volts for voltage and MHz for clocks) in the output.
                Defaults to False.
            timestamp (bool, optional): If True, prepends a timestamp to each line of the CSV string. Defaults to False.

        Returns
        ------
            str: A CSV formatted string representation of the current CPU status.
        """

        DATETIME_REGEX = re.compile(r'\d+(-|/)\d+(-|/)\d+\s\d+:\d+:\d+(\.\d+)?')
        header_ = ''

        unit_definitions = [' V', ' MHz', ' MHz', ' °C', ' °C']
        template = f"{self.voltage},{self.average_clock},{self.max_clock},{self.average_temp},{self.max_temp}"

        if timestamp:
            timestamp = str(datetime.datetime.now()).replace('-', '/')
            template = f"{timestamp},{template}"
        if header:
            if timestamp:
                keys = ['Time', 'Voltage', 'Average Clock', 'Max Clock', 'Average Temp', 'Max Temp']
            else:
                keys = ['Voltage', 'Average Clock', 'Max Clock', 'AVerage Temp', 'Max Temp']
            header_ = ",".join(keys)
            template = header_ + "\n" + template

        # Append units to the end of each field
        if units:
            # The offset is used to account for the fact that we are adding units after each field
            # rather than at the end of each field. Time allows us to skip the timestamp field when adding units.
            offset = 0
            # Ignore header when adding units
            if header_:
                values = template.replace(header_, '').lstrip().split(',')
            else:
                values = template.lstrip().split(',')
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

        # Format the template with the data from this instance of the class.
        formatted = template.format(
            voltage=self.voltage,
            average_clock=self.average_clock,
            max_clock=self.max_clock,
            average_temp=self.average_temp,
            max_temp=self.max_temp,
        )
        return formatted

        values = ''
        header_line = ''
        if header:
            header_line = 'voltage,average_clock,max_clock,max_temp,avg_temp\n'
        if timestamp:
            if header:
                header_line = f'timestamp, {header_line}'
            values = f'{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},'
        if units:
            values = f'{values}{self.voltage}v,{self.average_clock}MHz,{self.max_clock}MHz,'
            values += f'{self.max_temp}°C,{self.average_temp}°C'
        else:
            values = f'{values}{self.voltage},{self.average_clock},{self.max_clock},'
            values += f'{self.max_temp},{self.average_temp}'
        return header_line + values

    def __str__(self):
        """
        Provides a human-readable representation of the CPU status. This includes the current voltage, average clock speed, maximum clock speed, maximum temperature and average temperature.

        Returns
        -------
            str: A string representing the current state of the CPU in a readable format.
        """
        voltage = self.voltage
        average_clock = self.average_clock
        maxiumum_clock = self.max_clock

        maxiumum_temp = self.max_temp
        average_temp = self.average_temp

        return (
            f'Volts: {voltage}v\n'
            f'Avg clock: {average_clock}MHz\n'
            f'Max clock: {maxiumum_clock}MHz\n'
            f'Max temp: {maxiumum_temp}°C\n'
            f'Avg temp: {average_temp}°C'
        ).strip()


# Example usage
if __name__ == '__main__':
    cpu_data = CpuData()
    print(cpu_data)
    print(format(cpu_data, 'csv_units'))
    print(cpu_data.voltage)
