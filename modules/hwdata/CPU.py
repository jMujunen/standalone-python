#!/usr/bin/env python3

# TODO:
# *  - [x] Add suppport for specifying which CPU to query

import subprocess
import re
import datetime
import datetime

class CpuData:
    def __init__(self):
        self.type = 'CPU'
        self.clock_speed_regex = re.compile(r'(cpu MHz)\s+:\s+([\d.]+)')
        self.cpu_voltage_regex = re.compile(r'([^+]\d{1,3}\.\d{2,})')
        self.cpu_temp_regex = re.compile(r'(Core \d+).*(\d\d\.\d).*\(high.*\)')
        self.name_regex = re.compile(r'Model name:\s+(.*)')
        self.name = self.cpu_name(short=True)
        self.temp = self.average_temp
    def query_cpu_clocks(self):
        clock_dict = {}
        # Read the contents of /proc/cpuinfo
        with open ('/proc/cpuinfo', 'r') as f:
            raw_output = f.read()
            f.close()
        # Find all matches in the text
        matches = re.findall(self.clock_speed_regex, raw_output)

        # Process the matches into dictionary format
        count = 1
        for match in matches:
            clock_dict[count] = match[1]
            count += 1
        return clock_dict
    def query_cpu_temp(self):
        temp_dict = {}
        cpu_temperatures = subprocess.run(
            'sensors | grep Core',
            shell=True,
            capture_output=True,
            text=True
        ).stdout.strip()
        matches = re.findall(self.cpu_temp_regex, cpu_temperatures)

        # Process the matches into dictionary format
        count = 1
        for match in matches:
            temp_dict[count] = match[1]
            count += 1
        return temp_dict
    @property
    def voltage(self):
        cpu_voltage_subproccess = subprocess.run([
                "echo $(sensors | grep VIN3)"
                ],
                shell=True,
                stdout=subprocess.PIPE 
            ).stdout.decode("utf-8")
        raw_value = self.cpu_voltage_regex.search(cpu_voltage_subproccess).group(1)
        cpu_voltage = raw_value.strip()

        if len(cpu_voltage) == 4: 
            return round(float(cpu_voltage.strip()), 3)
        elif len(cpu_voltage) == 6:
            return round((float(cpu_voltage)/1000), 3)
        else:
            # Raise custom error
            raise Exception("Error: Voltage not found (requires a 4 or 6 digit number eg 1.25v or 600.00mV)")

    def cpu_clocks_list(self):
        self.query_clocks = self.query_cpu_clocks()
        return ([round(float(clock)) for clock in self.query_clocks.values()])
    def cpu_temp_list(self):
        self.query_temp = self.query_cpu_temp()
        return ([round(float(temp)) for temp in self.query_temp.values()])
    @property
    def average_temp(self):
        return round(sum(self.cpu_temp_list()) / len(self.cpu_temp_list()))
    @property
    def max_temp(self):
        return max(self.cpu_temp_list())
    @property
    def max_clock(self):
        return max(self.cpu_clocks_list())
    @property
    def average_clock(self):
        return round(sum(self.cpu_clocks_list()) / len(self.cpu_clocks_list()))
    def cpu_name(self, short=False):
        output = subprocess.run(
            'lscpu | grep "Model name"',
            shell=True,
            capture_output=True,
            text=True
        )
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
        header_line = ''
        if header:
            header_line = 'voltage,average_clock,max_clock,max_temp,avg_temp\n'
        if units:
            values = f'{self.voltage}v,{self.average_clock}MHz,{self.max_clock}MHz,'
            values += f'{self.max_temp}°C,{self.average_temp}°C'
        else:
            values = f'{self.voltage},{self.average_clock},{self.max_clock},'
            values += f'{self.max_temp},{self.average_temp}'

        if timestamp:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]
            values = f'{timestamp},{values}'
        return header_line + values

    def __str__(self):
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

    # Format to csv, optionally with units
    def __format__(self, format_spec):
        if format_spec == 'csv':
            return self.csv()
        elif format_spec == 'csv_header':
            return self.csv(header=True)
        elif format_spec == 'csv_units':
            return self.csv(units=True)
        elif format_spec == 'csv_timestamp':
            return self.csv(timestamp=True)
        elif format_spec == 'csv_timestamp_units':
            return self.csv(units=True)
        else:
            return self.csv(header=True, units=True)

# Example usage
if __name__ == '__main__':
    cpu_data= CpuData()
    print(cpu_data)
    print(format(cpu_data, 'csv_units'))
    print(cpu_data.voltage)
    print(format(cpu_data, 'csv_timestamp'))