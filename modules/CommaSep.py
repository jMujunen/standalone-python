#!/usr/bin/env python3

def add_commas(number):
    return '{:,}'.format(number)

# Example usage
result = add_commas(1000)
print(result)  # Output: 1,000
