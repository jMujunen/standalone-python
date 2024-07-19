#!/usr/bin/env python3
""""""

import re
import subprocess
import sys

RESET = "\033[0m"
RED, GREEN, BLUE, YELLOW = "\033[31m", "\033[32m", "\033[36m", "\033[33m"


class SMS:
    """
    Send SMS messages using KDE Connect CLI

    Attributes:
    -----------
        _device_id (str): Device ID of the phone to send SMS messages.
        _contacts (dict): Dictionary mapping contact names to phone numbers.

    Properties:
    ------------
        device_id (str): Device ID of the phone to send SMS messages.
        contacts (dict): Dictionary mapping contact names to phone numbers.

    Methods:
    --------
        send(str, str): Send an SMS message to a contact.
    """

    def __init__(self, dev_id=None):
        """
        Initialize SMS object with device ID (optional).

        Args:
        -----
            dev_id (str): Device ID of the phone according to kdeconnect.
        """
        self._device_id = dev_id
        self._contacts = {}

    @property
    def device_id(self) -> str:
        """
        Device ID of the phone according to kdeconnect.

        Returns:
        -------
            str: Device ID of the phone according to kde
        """
        if not self._device_id:
            dev_id_process = subprocess.run(
                "kdeconnect-cli -l --id-only",
                shell=True,
                capture_output=True,
                text=True,
            )
            if dev_id_process.returncode == 0:
                self._device_id = dev_id_process.stdout.strip()
            else:
                raise Exception(dev_id_process.stderr.strip())
        return self._device_id

    def send(self, msg: str, destination: str) -> int:
        """
        Send an SMS message to a contact.

        Args:
        -----
            msg (str): SMS message to send.
            destination (str): Contact name or number to send SMS message to.

        Returns:
        --------
            int: Return code of the subprocess.
        """
        if destination in self._contacts:
            destination = self._contacts.get(destination)
        elif re.compile(r"\d{10}").fullmatch(destination):
            pass
        else:
            raise ValueError(f"Invalid destination: {destination}")

        print(
            f"\033[33mAttempting send {RESET} {BLUE}{msg}{RESET}] to {RESET} {BLUE}{destination}{RESET}..."
        )
        send_sms_process = subprocess.run(
            f'kdeconnect-cli --send-sms "{msg}" --destination {destination} -d {self.device_id}',
            shell=True,
            capture_output=True,
            text=True,
        )
        return send_sms_process.returncode

    @property
    def contacts(self) -> dict:
        """Dictionary mapping contact names to phone numbers.

        Returns:
        --------
            dict: Dictionary of contact name (str) -> phone number (str).
        """
        return self._contacts

    @contacts.setter
    def contacts(self, contacts: dict) -> None:
        """
        Set the contacts dictionary.

        Args:
        ------
            contacts (dict): Dictionary mapping contact names to phone numbers.
        """
        self._contacts = contacts

    def __str__(self) -> str:
        """String representation of SMS object."""
        return str(self.__dict__)


# Example usage
def main(dest):
    def joke():
        return subprocess.run(f"curl {url}", shell=True, capture_output=True, text=True)

    com = SMS("d847bc89_cacd_4cb7_855b_9570dba7d6fa")
    url = "https://icanhazdadjoke.com"

    # Regenerate a new joke until the user says agrees to send it
    while True:
        try:
            new_joke = joke()
            if new_joke.returncode == 0:
                print(new_joke.stdout)
                answer = input("Send? [Y/n]:")
                # Regex
                if re.compile(r"[Yy]|^$").match(answer):
                    break
                    # msg successful if instance is True
                else:
                    continue
            else:
                print(f"{RED}Error getting joke: \n{new_joke.returncode}{RESET}")
                return 1
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            return 1

    if com.send(new_joke.stdout, dest) == 0:
        print(f"{GREEN}Success{RESET}")
        return 0
    else:
        print(f"{RED}Error sending msg: \n{new_joke.returncode}{RESET}")
        return 1


if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except IndexError:
        print("Usage:")
        print("sms.py <destination>")
