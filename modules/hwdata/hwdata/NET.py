#!/usr/bin/env python3

# Network.py - Query network information for HWINFO

import psutil
import subprocess

from dataclasses import dataclass


@dataclass
class Interface:
    def __init__(self, interface="wlan0"):
        self.interface = interface

    def addresses(self):
        for interface, values in psutil.net_if_addrs().items():
            if self.interface in interface:
                ip = values[0].address
                netmask = values[0].netmask
                broadcast = values[0].broadcast
                for item in values:
                    if item.family == 17:
                        mac = item.address
        return (ip, netmask, broadcast, mac)

    def connections(self):
        all_connections = psutil.net_connections(kind="inet")
        listening_connections = []

        established_connections = []
        outgoing_connections = []
        other_connections = []

        for conn in all_connections:
            # Filter remote addresses. Anything other than 127.0.0.1 is of note.
            # Outgoing is being defined as anything facing the internet
            # In reality, this could be incoming or outgoing
            try:
                if conn.raddr[0] != "127.0.0.1" and conn.laddr[0] != "127.0.0.1":
                    conn.laddr[0].strip("::ffff:")
                    conn.raddr[0].strip("::ffff:")
                    outgoing_connections.append(conn)
            except Exception as e:
                pass
            try:
                if conn.status == "LISTEN":
                    listening_connections.append(conn)
                elif conn.status == "ESTABLISHED":
                    established_connections.append(conn)
                elif conn.status == "TIME_WAIT":
                    pass
                else:
                    other_connections.append(conn)
            except Exception as e:
                pass

        return (
            listening_connections,
            established_connections,
            outgoing_connections,
            other_connections,
        )

    def byte_io(self, destination):
        if not self.interface in psutil.net_connections(pernic=True):
            return 1
        bytes_sent = psutil.net_io_counters().bytes_sent
        bytes_recv = psutil.net_io_counters().bytes_recv
        if destination == "sent":
            return bytes_sent
        elif destination == "recv":
            return bytes_recv
        else:
            return bytes_sent, bytes_recv

    def ping(self, destination="1.1.1.1"):
        ping = subprocess.run(
            f'ping -c 1 {destination} | sed -u "s/^.*time=//g; s/ ms//g; s/^PING.*//g; s/^---.*//g; s/^.*packets.*//g; s/^rtt.*//g"',
            shell=True,
            capture_output=True,
            text=True,
        )
        if ping.stderr:
            return ping.stderr.strip()
        try:
            return round(float(ping.stdout.strip()))
        except ValueError:
            return 0

    @property
    def online(self):
        return "online" if psutil.net_if_stats()[self.interface].isup else "offline"

    """
    def port_info(self, verbose_level=0, host='10.0.0.1', entire_subnet=False):
        # Verbose levels:
        # 0 - Show which ports are open
        # 1 - Show which ports are open,their services and versions
        # 2 - Show everything -- WARNING: This can take a while
        nm = nmap.PortScanner()
        print('Scanning...')

        if entire_subnet:
            nm.scan(host, arguments='-sn')
        else:
            nm.scan(host, arguments='-sP')

        if verbose_level == 0:
            nm.scan(host, arguments='-sS')
        elif scan == 'services':
            nm.scan(host, arguments='-sV')
            for host in nm.all_hosts():
                for protocol in nm[host].all_protocols():
                    lport = nm[host][protocol].keys()
                    for port in lport:
                        service = nm[host][protocol][port]['name']
                        version = nm[host][protocol][port]['version']

        return nm
        """

    @property
    def hosts(self):
        hosts = subprocess.run(
            'nmap -T4 -sn 10.0.0.0/24 | grep "Nmap"',
        )

    def __str__(self):
        return str(
            f'Interface: {self.interface} : {self.online}\n\n'
            f'Connections:\n'
            f'Listening connections: {len(self.connections()[0])}\n'
            f'Established connections: {len(self.connections()[1])}\n'
            f'Outgoing connections: {len(self.connections()[2])}\n'
            f'Other connections: {len(self.connections()[3])}\n\n'
            f'Ping: {self.ping("1.1.1.1")} ms\n\n'
            f'Addresses:\n'
            f'  IP: {self.addresses()[0]}\n'
            f'  Netmask: {self.addresses()[1]}\n'
            f'  Broadcast: {self.addresses()[2]}\n'
            f'  MAC: {self.addresses()[3]}'
        )

    # TODO: Add more
    """
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        print(proc.info)
    """


# Example
if __name__ == "__main__":
    net = Interface()
    print(net)

    try:
        listen_addr = []
        listen_addr = [
            [
                k
                for k in net.connections()[0]
                if k.raddr[0] != "127.0.0.1" and k.laddr not in listen_addr
            ],
            [
                k
                for k in net.connections()[0]
                if k.laddr[0] != "127.0.0.1" and k.laddr not in listen_addr
            ],
        ]
    except Exception as e:
        print(e)
    try:
        established_addr = []
        established_addr = [
            [
                k
                for k in net.connections()[1]
                if k.raddr[0] != "127.0.0.1" and k.laddr not in established_addr
            ],
            [
                k
                for k in net.connections()[1]
                if k.laddr[0] != "127.0.0.1" and k.laddr not in established_addr
            ],
        ]
    except Exception as e:
        print(e)

    try:
        outgoing_addr = []
        outgoing_addr = [
            [
                k
                for k in net.connections()[2]
                if k.raddr[0] != "127.0.0.1" and k.laddr not in outgoing_addr
            ],
            [
                k
                for k in net.connections()[2]
                if k.laddr[0] != "127.0.0.1" and k.laddr not in outgoing_addr
            ],
        ]

    except Exception as e:
        print(e)

    raddr = []
    for k in net.connections()[2]:
        if k.raddr[0] not in raddr:
            raddr.append(f"remote: {k.raddr[0]}")
        if k.laddr[0] not in raddr:
            raddr.append(f"local: {k.laddr[0]}")
    import pprint

    pprint.pprint(raddr)

    for k in net.connections()[0]:
        try:
            if k.raddr[0] not in listen_addr:
                listen_addr.append(f"remote: {k.raddr[0]}")
            if k.laddr[0] not in listen_addr:
                listen_addr.append(f"local: {k.laddr[0]}")
        except Exception as e:
            pass

    for k in net.connections()[3]:
        try:
            if k.raddr[0] not in outgoing_addr:
                outgoing_addr.append(f"remote: {k.raddr[0]}")
            if k.laddr[0] not in outgoing_addr:
                outgoing_addr.append(f"local: {k.laddr[0]}")
        except Exception as e:
            print(e, end=",")
            pass

    import pprint

    try:
        for k in established_addr:
            pprint.pprint(k)
    except Exception as e:
        print(e)
    try:
        for k in listen_addr:
            pprint.pprint(k)
    except Exception as e:
        print(e)

    try:
        for k in outgoing_addr:
            pprint.pprint(k)
    except Exception as e:
        print(e)
