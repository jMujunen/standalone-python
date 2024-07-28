#!/usr/bin/env python3

from time import sleep
import argparse
import os

from hwdata import CPU


def parse_args():
    parser = argparse.ArgumentParser(
        description="Outputs CPU data in csv form and logs it to a file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=0.5,
        help="Interval between measurements in seconds.",
    )
    parser.add_argument(
        "-t",
        "--time",
        type=int,
        default=60,
        help="Time in seconds to run the script.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to output file.",
    )
    parser.add_argument(
        "--nostop",
        action="store_true",
        help="Continue forever or until CTRL+C is pressed.",
        default=False,
    )
    parser.add_argument(
        "-1",
        "--oneline",
        action="store_true",
        help=("Don't show the header, and print with end='\r'"),
        default=False,
    )
    return parser.parse_args()


def log_cpu(args):
    if not args.nostop:
        count = round(args.time / args.interval)
    else:
        count = 0
    if not args.output:
        output_file = "/tmp/cpu.csv"
    else:
        output_file = args.output

    line = "datetime,voltage,average_clock,max_clock\n"

    if not os.path.exists(output_file):
        with open(output_file, "w") as file:
            file.write(line)
            file.close()
    print(
        f"[\033[38;2;57;206;196m {count} \033[0m] " f"\033[1;32m {line.strip()} \033[0m",
        end="\n",
    )

    if args.nostop:
        count += 1
    else:
        count -= 1

    cpu_data = CPU.CpuData()
    if args.oneline:
        end = "\r"
        try:
            os.system("clear")
        except Exception:
            os.system("cls")
    else:
        end = "\n"

    while count > -1:
        try:
            line = format(cpu_data, "csv_timestamp")
            columns = line.split(",")

            colored_ouput = (
                f"[\033[38;2;57;206;196m {count:>3} \033[0m] "
                f"\033[1;32m {columns[0].strip()} \033[0m"
                f"\033[38;5;208m {columns[1].strip():>6} \033[0m"
                f"\033[1:33m {columns[2].strip():>4} \033[0m"
                f"\033[1;33m {columns[3].strip():>4} \033[0m"
                f"\033[1;31m  {columns[4].strip():>2} \033[0m"
                f"\033[1;31m  {columns[5].strip():>2} \033[0m\n"
            )
            print(f"{colored_ouput.strip()}", end=end)
            # Write data to file
            with open(output_file + ".sh", "a") as file:
                file.write(colored_ouput)
                file.close()
            with open(output_file, "a") as file:
                file.write(f"{line}\n")
                file.close()
            if args.nostop:
                count += 1
            else:
                count -= 1

            sleep(args.interval)
        except KeyboardInterrupt:
            print("Exiting...")
            break


if __name__ == "__main__":
    args = parse_args()
    log_cpu(args)
