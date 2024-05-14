#!/usr/bin/env python3

import subprocess
import re

class GpuData:
    def __init__(self):
        self.type = 'GPU'
        self.temp = self.core_temp
        self.name = self.gpu_name(short=True)
    @property
    def core_temp(self):
        # temperature.gpu
        core_temp = subprocess.run(
            'nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader',
            shell=True,
            capture_output=True,
            text=True
        ).stdout.strip()
        return core_temp
    @property
    def memory_temp(self):
        # temperature.memory
        memory_temp = subprocess.run(
            'nvidia-smi --query-gpu=temperature.memory --format=csv,noheader',
            shell=True,
            capture_output=True,
            text=True
        ).stdout.strip()
        return memory_temp
    @property
    def core_clock(self):
        # clocks.current.graphics
        core_clock = subprocess.run(
            'nvidia-smi --query-gpu=clocks.current.graphics --format=csv,noheader',
            shell=True,
            capture_output=True,
            text=True
        ).stdout.replace('MHz','').strip()
        return core_clock
    @property
    def max_core_clock(self):
        # clocks.max.graphics
        core_usage = subprocess.run(
            'nvidia-smi --query-gpu=clocks.max.graphics --format=csv,noheader',
            shell=True,
            capture_output=True,
            text=True
        ).stdout.replace('MHz','').strip()
        return core_clock
    @property
    def memory_clock(self):
        # clocks.current.memory
        memory_clock = subprocess.run(
            'nvidia-smi --query-gpu=clocks.current.memory --format=csv,noheader',
            shell=True,
            capture_output=True,
            text=True
        ).stdout.replace('MHz','').strip()
        return memory_clock
    @property
    def max_memory_clock(self):
        # clocks.max.memory
        core_usage = subprocess.run(
            'nvidia-smi --query-gpu=clocks.max.memory --format=csv,noheader',
            shell=True,
            capture_output=True,
            text=True
        ).stdout.replace('MHz','').strip()
        return memory_clock
    @property
    def memory_usage(self):
        memory_usage = subprocess.run(
            'nvidia-smi --query-gpu=utilization.memory --format=csv,noheader',
            shell=True,
            capture_output=True,
            text=True
        ).stdout.replace('%','').strip()
        return memory_usage
    @property
    def voltage(self):
        voltage_regex = re.compile(r'(\d+.\d+)')
        voltage_subprocess = subprocess.run(
            'nvidia-smi -q --display=Voltage | grep -o -P "Graphics.*"',
            shell=True,
            capture_output=True,
            text=True
        ).stdout.strip()
        matches = ' '.join(voltage_regex.findall(voltage_subprocess))
        volts = round(float(matches)/ 1000, 2)
        return float(volts)
    @property
    def power(self):
        # power.draw
        power = subprocess.run(
            'nvidia-smi --query-gpu=power.draw --format=csv,noheader',
            shell=True,
            capture_output=True,
            text=True
        ).stdout.replace('W','').strip()
        return round(float(power))
    @property
    def core_usage(self):
        core_usage = subprocess.run(
            'nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader',
            shell=True,
            capture_output=True,
            text=True
        ).stdout.replace('%','').strip()
        return core_usage
    def average_fps(self):
        average_fps = subprocess.run(
            'nvidia-smi --query-gpu=encoder.stats.averageFps --format=csv,noheader',
            shell=True,
            capture_output=True,
            text=True
        ).stdout.strip()
        return average_fps
    def average_latency(self):
        average_latency = subprocess.run(
            'nvidia-smi --query-gpu=encoder.stats.averageLatency --format=csv,noheader',
            shell=True,
            capture_output=True,
            text=True
        ).stdout.strip()
        return average_latency
    @property
    def fan_speed(self):
        fan_speed = subprocess.run(
            'nvidia-smi --query-gpu=fan.speed --format=csv,noheader',
            shell=True,
            capture_output=True,
            text=True
        ).stdout.strip()
        return fan_speed

    def gpu_name(self, short=False):
        name_regex = re.compile(r'(AMD|NVIDIA|Intel)\s?(\s?GeForce\s?|\s?Radeon\s?)\s?(\sGTX\s?|\s?RTX\s?)(.*)')
        subout = subprocess.run(
            'nvidia-smi --query-gpu=name --format=csv,noheader',
            shell=True,
            capture_output=True,
            text=True
        ).stdout.strip()
        matches = name_regex.findall(subout)
        if short:
            self.name = matches[0][-1]
        else:
            self.name = ' '.join(matches[0])
        return self.name
    @property
    def timestamp(self):
        timestamp = subprocess.run(
            'nvidia-smi --query-gpu=timestamp --format=csv,noheader',
            shell=True,
            capture_output=True,
            text=True
        ).stdout.strip()
        return timestamp
    @property
    def speed(self):
        return self.fan_speed.replace('%','').strip()
    def __str__(self):
        return (
        f'GPU: {self.name}\n'
        f'Core Temp: {self.core_temp} °C\n'
        f'Core Clock: {self.core_clock} MHz\n'
        f'Memory Clock: {self.memory_clock} MHz\n'
        f'Memory Usage: {self.memory_usage} %\n'
        f'Core Usage: {self.core_usage} %\n'
        f'Power: {self.power} W\n'
        f'Average FPS: {self.average_fps()} FPS\n'
        f'Average Latency: {self.average_latency()} ms\n'
        f'Fan Speed: {self.fan_speed}\n'
        f'Voltage: {self.voltage} V\n'
        ).strip()
        # Memory Temp: {self.memory_temp()} °C
    def __lower__(self):
        return ''.join(self.name).lower()

    def __upper__(self):
        return self.name.upper()
# Example
if __name__ == '__main__':
    gpu = GpuData()
    print(f'Full GPU Name: {gpu.gpu_name()}')
    print(f'Short GPU Name: {gpu.gpu_name(short=True)}')
    print(str(gpu))
