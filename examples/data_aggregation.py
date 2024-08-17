#!/usr/bin/env python3

# data_aggregation.py - Example for aggregating data in memory before writing to a CSV file

import csv


class DataAggregator:
    def __init__(self, file: str, chunk_size: int = 1000):
        """
        Initializes a new instance of the class with the given path to a CSV file.

        Parameters:
        ------------
        >>>  path_to_file -> str: The path to the CSV file.

        Returns:
            None
        """
        self.path = file
        self.chunk_size = chunk_size
        self.data = []

    def chunk(self, new_data: str):
        """Stores the data in memory until the configured size."""
        self.data.append(new_data)

    def write(self):
        """Writes data to a CSV file in chunks"""
        with open(self.path, "w", newline="") as csvfile:
            csv_writer = csv.writer(csvfile)
            for row in self.data:
                csv_writer.writerow(row)

    def read(self):
        """Reads aggregated data from a CSV file."""
        with open(self.path) as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                self.chunk(row)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Exiting context manager.", f"Writing {len(self.data)} rows to '{self.path}'.")
        if exc_type:
            print(f"An error occurred: {exc_val}")
            return True
        return False


# Example usage
if __name__ == "__main__":
    # Create a new instance of the DataAggregator class
    aggregator = DataAggregator(input("Enter path to CSV file: "))
    # Read data from the CSV file
    aggregator.read()

    # Example usage
    for i in range(1000):  # Simulating data logging over time
        new_data = ["Sample", i, "Location"]
        accumulate_data(new_data)

        # Conditionally write aggregated data to the file
        if i % 100 == 0:  # Adjust the condition based on your specific use case
            write_aggregated_data_to_csv()
            aggregated_data = []  # Clear the aggregated data for the next batch
