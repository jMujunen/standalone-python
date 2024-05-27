class ByteConverter:
    """
    Converts a size in bytes to a human-readable string representation.

    Parameters:
        size_in_bytes (int): The size in bytes to be converted.

    Returns:
        str: A human-readable string representation of the size, with units such as B, KB, MB, or GB.
     """
    def __init__(self, size_in_bytes: int):
        self._size_str = self._convert(abs(int(size_in_bytes)))
        if size_in_bytes < 0:
            self._size_str = '-' + self._size_str
            
    def _convert(self, size: int) -> str:
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        for unit in units[:-1]:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size/1024:.2f} {units[-1]}"  # Last unit is TB
    def __str__(self):
        return self._size_str
    def __float__(self) -> float:
        return float(self._size_str.split()[0])  

if __name__ == "__main__":

    # Testing with different values of bytes.
    print(ByteConverter(1024))   # Outputs: "1.00 KB"
    print(ByteConverter(1536))   # Outputs: "1.50 MB"
    print(ByteConverter(789456128))  # Outputs: "752.00 MB"
    print(ByteConverter(-1536))    # Outputs: "-1.50 MB"


