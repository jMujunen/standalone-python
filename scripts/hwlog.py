#!/usr/bin/env python3

# csv_output.py - CSV output of various metrics

import os
import sys
import datetime
from time import sleep
import argparse
from hwdata import CPU, GPU, NET, SYS

HEADER = "datetime, cpu_voltage, cpu_temp, cpu_max_clock, cpu_avg_clock, \
gpu_temp, gpu_power, gpu_voltage, gpu_usage, gpu_mem_usage,gpu_core_clock, gpu_mem_clock, \
ram_usage, system_temp, ping"

cpu_data = CPU.CpuData()
gpu_data = GPU.GpuData()
network_data = NET.NetworkInterface()
sys_data = SYS.SystemTemp()
ram_data = SYS.RAM()

def parse_args():
    parser = argparse.ArgumentParser(
        description="CSV output of various metrics",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-f", "--file",
        help="Path to the csv file",
        type=str,
        default="/tmp/hwlog.csv"
    )
    parser.add_argument(
        '-i', '--interval',
        help="Polling interval in seconds",
        type=float,
        default=1
    )
    parser.add_argument(
        '-s', '--show',
        help="Show output",
        action='store_true'
   )
   # TODO:
   # ! Add options for selecting which metrics to show
    return parser.parse_args()
def main(OUTPUT_FILE, POLL_INTERVAL):
    timestamp = str(datetime.datetime.now())[:-7]
    COLUMNS = [ timestamp,
                cpu_data.voltage,
                cpu_data.max_temp,
                cpu_data.max_clock,
                cpu_data.average_clock,
                gpu_data.temp,
                gpu_data.power,
                gpu_data.voltage,
                gpu_data.core_usage,
                gpu_data.memory_usage,
                ram_data.percent_used,
                sys_data.temp,
                network_data.ping(),
                gpu_data.core_clock,
                gpu_data.memory_clock ]

    while True:
        try:
            line = "{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(*COLUMNS)
            if args.show:
                print(line)
            with open(OUTPUT_FILE, 'a') as f:
                f.write(line + '\n')
            sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(e)
            sys.exit(4)

if __name__ == '__main__':
    try:
        args = parse_args()
        OUTPUT = args.file
        POLL_INTERVAL = args.interval
        if args.show:
            print(HEADER)
        with open(OUTPUT, 'w') as f:
            f.write(HEADER + '\n')
            os.chmod(OUTPUT, 0o644)
        main(OUTPUT, POLL_INTERVAL)
    except PermissionError:
        sys.exit(5)
    except Exception as e:
        print(e)
        sys.exit(1)

