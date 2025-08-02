#!/usr/bin/env python3
import sqlite3
from collections import defaultdict


class SQLParser:
    def __init__(self, path: str):
        self.path = path

    def __enter__(self) -> "SQLParser":
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()
        self.tables = self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        )
        self.tables = [table[0] for table in self.tables]
        print("Tables:", self.tables)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.conn.close()

    def dict(self, table: str) -> dict:
        """Parse an SQL file and return a dictionary.

        Args:
        -----------
            table : str
                The name of the table to parse.
        Returns
        --------
            dict : dict
                A dictionary containing the parsed data.
        """
        # Connect to the SQLite database
        data = defaultdict(list)
        self.cursor.execute(f"SELECT * FROM {table}")
        columns = [description[0] for description in self.cursor.description]
        for row in self.cursor.fetchall():
            data[table].append(dict(zip(columns, row, strict=False)))
        return data


def convert_sql_to_python(database_path: str) -> defaultdict[str, list]:
    """Convert an SQLite database to a Python dictionary.

    Parameters
    -----------
        database_path : str
            The path to the SQLite database file.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Create a dictionary to hold the data
    data = defaultdict(list)

    # Fetch data from the "employees" table
    cursor.execute("SELECT * FROM employees")
    rows = cursor.fetchall()
    for row in rows:
        employee = {
            "id": row[0],
            "name": row[1],
            "department_id": row[2],
            # Add more columns as needed
        }
        data["employees"].append(employee)

    # Fetch data from the "departments" table
    cursor.execute("SELECT * FROM departments")
    rows = cursor.fetchall()
    for row in rows:
        department = {
            "id": row[0],
            "name": row[1],
            # Add more columns as needed
        }
        data["departments"].append(department)

    # Close the database connection
    conn.close()

    return data


# Example usage:
# database_path = 'path_to_your_database.db'
# python_data = convert_sql_to_python(database_path)
# print(python_data)
