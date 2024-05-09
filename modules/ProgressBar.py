#!/usr/bin/env python3

from time import sleep

# pb.py - A simple progress bar object

class ProgressBar:
    """
    A simple progress bar object

    Attributes
    ----------
    inital_value : int
        The initial value of the progress bar. Defaults to 100.

    current_value : int
        The current value of the progress bar.

    Methods
    -------
    update(current_value=0)
        Updates the progress bar with the given current value

    increment(increment=1)
        Increments the current value of the progress bar by the given amount

    value(value)
        Sets the current value of the progress bar to the given value
    
    len()
        Returns the value of the progress bar for use in a for loop
    """

    def __init__(self, inital_value=100):
        """
        Initializes a new instance of the class

        Parameters
        ----------
        inital_value : int
            The initial value of the progress bar. Defaults to 100.
        """
        self.inital_value = inital_value
        self.value_ = 0

    def update(self, current_value=0):
        """
        Updates the progress bar with the given current value

        Parameters
        ----------
        current_value : int
            The value to update the progress bar with
        """
        self.progress = current_value / self.inital_value * 100
        output = str(f"[{self.progress:.1f}%]")
        print(output.ljust(int(self.progress), '='), end='[100.0%]\r')

    def increment(self, increment=1):
        """
        Increments the current value of the progress bar by the given amount

        Parameters
        ----------
        increment : int
            The amount to increment the current value by
        """
        self.value = self.value + increment
        self.update(self.value)
    @property
    def value(self):
        """
        This is a property method that returns the current value of the progress bar

        Returns
        -------
        int
            The current value of the progress bar.
        """
        return int(self.value_)

    @value.setter
    def value(self, new_value):
        """
        Method which sets the value of the progress bar

        Args
        ------
        new_value : int
            The new value to set for the progress bar.
        """
        self.value_ = new_value
        self.update(self.value_)
    def __len__(self):
        """Returns the length of the progress bar for use in a for loop"""
        return self.inital_value

# Example usage
if __name__ == '__main__':
    pb = ProgressBar(100)
    for i in range(100):
        pb.increment()
        sleep(0.1)
    