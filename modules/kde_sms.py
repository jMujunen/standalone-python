#!/usr/bin/env python3

import subprocess
import sys




class SMS:

def send_sms(destination, msg):
    dev_id = subprocess.run(
        'kdeconnect-cli -l --id-only',
        shell=True,
        capture_output=True,
        text=True
    )

    if dev_id.returncode != 0:
        print('Error getting device ID')
        sys.exit(1)
    else:
        sendsms_output = subprocess.run(
            f'kdeconnect-cli --send-sms "{msg}" --destination {destination} -d {dev_id.stdout}',
            shell=True
    )
    return 0
