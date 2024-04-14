#!/usr/bin/env python

import threading
import time
import sys

from Notification import Notification
class Pomo():
    def __init__(self, duration=25):
        self.duration = duration * 60
        self.t = threading.Thread(target=self.start)

    def start(self):
        self.t.start()
    def __str__(self):
        return f'{self.duration / 60}'
    def __int__(self):
        return round(self.duration)
# Example
if __name__ == "__main__":
    try:
        timer = Pomo(int(sys.argv[1]))
    except Exception as e:
        timer = Pomo()
    inttimer = int(timer)
    while inttimer > 0:
        minutes = inttimer / 60
        print(minutes, end='\r')
        inttimer -= 1
        time.sleep(1)
        
Notification("Pomodoro", "Time's up!", 3000).show()
