#!/usr/bin/env python3

# dadjoke2sms.py - Send dad jokes on a somewhat regular basis

import subprocess
from typing import Optional, Dict
class SMS:
    def __init__(self, device_id: Optional[str] = None):
        self._device_id = device_id
        self._contacts: Dict[str, str] = {}
        self._events = []
    @property
    def device_id(self) -> str:
        if not self._device_id:
            dev_id_process = subprocess.run(
                'kdeconnect-cli -l --id-only',
                shell=True,
                capture_output=True,
                text=True
            )
            if dev_id_process.returncode == 0:
                self._device_id = dev_id_process.stdout.strip()
            else:
                raise Exception(dev_id_process.stderr.strip())
        return self._device_id

    def send(self, msg: str, destination: str) -> str:
        destination_number = self._contacts.get(destination)
        if not destination_number:
            raise ValueError(f"Invalid destination: {destination}")

        print(f'\033[33m[Attempting send to {destination_number}]\033[0m...')
        send_sms_process = subprocess.run(
            f'kdeconnect-cli --send-sms "{msg}" --destination {destination_number} -d {self.device_id}',
            shell=True,
            capture_output=True,
            text=True
        )
        self._events.append(send_sms_process)
        if send_sms_process.returncode == 0:
            return send_sms_process.stdout.strip()
        else:
            raise Exception(send_sms_process.stderr.strip())
    
    @property
    def contacts(self) -> Dict[str, str]:
        return self._contacts

    @contacts.setter
    def contacts(self, contacts: Dict[str, str]):
        self._contacts = contacts

def main():
    sms_obj = SMS('d847bc89_cacd_4cb7_855b_9570dba7d6fa')
    print(sms_obj)
    print(sms_obj.device_id)

    sms_obj.contacts = {'me': '6042265455', 'muru': '6048359467'}

    try:
        sms_obj.send('Hello', 'me')
        print(sms_obj)
        sms_obj.send('Hello', 'me')
        print(sms_obj)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()