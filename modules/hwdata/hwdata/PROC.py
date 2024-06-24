#!/usr/bion/env python3

# PROC.py - Query process information for HWINFO

import psutil
from time import sleep
import threading
from dataclasses import dataclass


@dataclass(frozen=True)
class Proc:
    def __init__(self, pid=None):
        self.pid = pid
        self.t = threading.Thread(target=self.sigterm_wait, args=(self.pid))

    def info(self):
        return psutil.Process(self.pid)

    """
    def terminate_all(self, pname=self.info().name()):
        for p in psutil.process_iter(["name","exe","cmdline"]):
            if pname in p.info.name() or pname in p.info.exe() or pname in p.info.cmdline():
                if p.is_running():
                    p.terminate()
        self.t.start()
    """

    def sigterm_wait(self):
        sleep(7)
        self.kill_all()

    """
    def kill_all(self, pname=self.info().name()):
        for p in psutil.process_iter(["name","exe","cmdline"]):
            if pname in p.info.name() or pname in p.info.exe() or pname in p.info.cmdline():
                if p.is_running():
                    p.terminate()
    """

    def __str__(self):
        return self.info().name()
