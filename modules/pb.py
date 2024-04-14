#!/usr/bin/env python3

# pb.py - A simple progress bar object

class ProgressBar:
    def __init__(self, inital_value=100):
        self.inital_value = inital_value
        self.current_value = 0
    def update(self, current_value=0):
        if current_value == 0:
            self.current_value = self.current_value
        else:
            self.current_value = current_value
        self.progress = current_value / self.inital_value * 100
        output = str(f"[{self.progress:.1f}%]")
        print(output.ljust(int(self.progress), '='), end='[100.0%]\r')

    def increment(self, increment=1):
        self.current_value += increment
        self.update(self.current_value)
    
    def set_value(self, value):
        self.current_value = value
        self.update(self.current_value)
