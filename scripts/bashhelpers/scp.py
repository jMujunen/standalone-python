#!/usr/bin/env python3

import argparse
import subprocess

global hosts

hosts = {
    'osmc': 'osmc@10.0.0.87',
    'pihole': 'joona@10.0.0.132',
}

def parse_args():
    parser = argparse.ArgumentParser(
        description='scp a file',

    )
    parser.add_argument('HOST', type=str, 
        help='Host to scp to - Either hostname@ip or hostname')
    parser.add_argument('SOURCE_PATH', type=str, help='Source path', nargs='+')
    parser.add_argument('DEST_PATH', type=str, help='Destination path', nargs='+')

    args = parser.parse_args()
    if args.HOST in hosts:
        args.HOST = hosts[args.HOST]
    else:
        print(f'Host {args.HOST} not found')
    return args


def main(args):
    source_files = ' '.join(args.SOURCE_PATH)
    source_dest = ' '.join(args.DEST_PATH)
    output = subprocess.run(
        f'scp {source_files} {args.HOST}:{source_dest}',
        shell=True,
        text=True,
        capture_output=True,
        )
    error = output.stderr
    out = output.stdout
    if error:
        print(error)
        exit(1)
    else:
        # Print colored msg
        print(f'\x1b[1;32mSucess\033[0m')
    exit(0)


if __name__ == '__main__':
    args = parse_args()
    main(args)