#!/usr/bin/env python

import subprocess

from CPU import CpuData

cpu_data = CpuData()

print(cpu_data.csv(units=True))

subprocess.run(
    f"echo {cpu_data.csv(units=True)} >> /tmp/cpu_data_timestamp.csv",
    shell=True
)
