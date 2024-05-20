class ByteConverter:
    """
    Converts a size in bytes to a human-readable string representation.

    Parameters:
        size_in_bytes (int): The size in bytes to be converted.

    Returns:
        str: A human-readable string representation of the size, with units such as B, KB, MB, or GB.
    """

    def __init__(self, size_in_bytes):
        self.size_in_bytes = self(size_in_bytes)

    def __call__(self, size_in_bytes):
        self.size_in_bytes = int(size_in_bytes)
        if size_in_bytes < 1024:
            return f"{size_in_bytes} B"
        elif size_in_bytes < 1024**2:
            return f"{size_in_bytes / 1024:.2f} KB"
        elif size_in_bytes < 1024**3:
            return f"{size_in_bytes / (1024**2):.2f} MB"
        else:
            return f"{size_in_bytes / (1024**3):.2f} GB"

    def __str__(self):
        return str(self.size_in_bytes)


# Example usage:
if __name__ == "__main__":
    bytes = ByteConverter()
