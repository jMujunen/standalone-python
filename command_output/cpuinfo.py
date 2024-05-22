#!/usr/bin/env python3

import subprocess

from CPU import CpuData

cpu_data = CpuData()

print(cpu_data.csv(units=True))

subprocess.run(
    f"echo {cpu_data.csv(units=True)} >> /tmp/cpuinfo.csv",
    shell=True
)
