#!/usr/bin/env python3

from time import sleep

# pb.py - A simple progress bar object

class ProgressBar:
    """
    A simple progress bar object

    Attributes
    ----------
    inital_value : int
        The maximum value of the progress bar
    current_value : int
        The current value of the progress bar

    Methods
    -------
    update(current_value=0)
        Updates the progress bar with the given current value

        Parameters
        ----------
        current_value : int
            The value to update the progress bar with

    increment(increment=1)
        Increments the current value of the progress bar by the given amount

        Parameters
        ----------
        increment : int
            The amount to increment the current value by

    value(value)
        Sets the current value of the progress bar to the given value

        Parameters
        ----------
        value : int
            The value to set the current value to
    """
    def __init__(self, inital_value=100):
        """
        Initializes the progress bar object

        Parameters
        ----------
        inital_value : int
            The maximum value of the progress bar (default is 100)
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

        Returns
        -------
        None
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

        Returns
        -------
        None
        """
        self.value = self.value + increment
        self.update(self.value)

    @property
    def value(self):
        """
        This is a property method that returns the current value of the progress bar.

        Returns:
            int: The current value of the progress bar.
        """
        return int(self.value_)

    @value.setter
    def value(self, new_value):
        """
        Method which sets the value of the progress bar.

        Args:
            new_value (int): The new value to set for the progress bar.
        """
        self.value_ = new_value
        self.update(new_value)

# Example usage
if __name__ == '__main__':
    pb = ProgressBar(100)
    for i in range(100):
        pb.increment()
        sleep(0.1)
    