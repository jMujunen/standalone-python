"""This module exposes the Log class as a parent of File"""

from ExecutionTimer import ExecutionTimer

with ExecutionTimer():
    print('Log')
    import re
    import pandas as pd
    from .GenericFile import File

    # from fsutils.GenericFile import File
    from Color import fg, style

    class Log(File):
        """
        A class to represent a hwlog file.

        Attributes:
        ----------
            path (str): The absolute path to the file.
            spec (str, optional): The delimiter used in the log file. Defaults to 'csv'.
            encoding (str, optional): The encoding scheme used in the log file. Defaults to 'iso-8859-1'.

        Methods:
        ----------
            header (str): Get the header of the log file.

            columns (list): Get the columns of the log file.

            footer (str): Get the footer of the log file.

        """

        def __init__(self, path, spec="csv", encoding="iso-8859-1"):
            self.DIGIT_REGEX = re.compile(r"(\d+(\.\d+)?)")
            specs = {"csv": ",", "tsv": "\t", "custom": ", "}
            self.spec = specs[spec]
            super().__init__(path, encoding)

        @property
        def header(self):
            """
            Get the header of the log file.

            Returns:
            --------
                str: The header of the log file.
            """
            return self.head(1).strip().strip(self.spec)

        @property
        def columns(self):
            """
            Get the columns of the log file.

            Returns:
            --------
                list: Each column of the log file.
            """
            return [col for col in self.head(1).split(self.spec)]

        @property
        def footer(self):
            second_last, last = self.tail(2).strip().split("\n")
            second_last = second_last.strip(self.spec)
            last = last.strip(self.spec)
            return second_last if second_last == self.header else None

        def to_df(self):
            """
            Convert the log file into a pandas DataFrame.

            Returns:
            --------
                pd.DataFrame: The data of the log file in a DataFrame format.
            """
            import pandas as pd

            return pd.DataFrame(self.content, columns=self.columns)

        def sanatize(self):
            """
            Sanatize the log file by removing any empty lines, spaces, and trailing delimiters
            from the header and footer. Also remove the last 2 lines

            Returns:
            -------
                str: The sanatized content
            """
            pattern = re.compile(
                r"(GPU2.\w+\(.*\)|NaN|N\/A|Fan2|°|Â|\*|,,+|\s\[[^\s]+\]|\"|\+|\s\[..TDP\]|\s\[\]|\s\([^\s]\))"
            )
            pattern = re.compile(r"(,\s+|\s+,)")

            sanatized_content = []
            lines = len(self)
            for i, line in enumerate(self):
                if i == lines - 2:
                    break
                sanatized_line = re.sub(pattern, "", line).strip().strip(self.spec)
                if sanatized_line:
                    sanatized_line = re.sub(pattern, ",", sanatized_line)
                    sanatized_line = re.sub(r"(\w+)\s+(\w+)", r"\1_\2", sanatized_line)
                    sanatized_content.append(sanatized_line)

            self._content = "\n".join(sanatized_content)
            return self._content

        @property
        def stats(self):
            """
            Calculate basic statistical information for the data in a DataFrame.

            Returns:
            --------
                pandas.Series: A series containing the mean, min, and max values of each column in the DataFrame.
            """
            try:
                df = pd.read_csv(self.path)
            except UnicodeDecodeError:
                df = pd.read_csv(self.sanatize())
            return df.mean()

        def compare(self, other):
            """
            Compare the statistics of this log file with another. Prints a table comparing each column's mean values.

            Parameters:
            -----------
                other (Log): Another Log instance to compare against.

            """

            # FIXME : Account for differences in columns. Currently, differences in columns output the following:
            """ 12V                              + 44                  11.94
                Vcore                            1.287               + 1.301
                VIN3                             + 55                  1.315
                GPU_Temperature                  + 70                     55
                GPU_Clock                        + 2575                 1964
                Frame_Time                       4.07                 + 8.73
                GPU_Busy                         + 58                  4.749 """

            def compare_values(num1, num2):
                digits = re.compile(r"(\d+(\.\d+)?)")

                num1 = digits.search(str(num1))[0]
                num2 = digits.search(str(num2))[0]
                # num2 = re.search(r'(\d+(\.\d+)?)', line.split(' ')[-1]).group(0)
                if float(num1) == float(num2):
                    return (
                        f"{num1.replace(num1, f'{fg.cyan}{'\u003d'}{style.reset} {str(num1)}')}",
                        num2,
                    )
                if float(num1) > float(num2):
                    return (
                        f"{num1.replace(num1, f'{fg.red}{'\u002b'}{style.reset} {str(num1)}')}",
                        num2,
                    )
                return (
                    num1,
                    f"{num2.replace(num2, f' {fg.red}{'\u002b'}{style.reset} {str(num2)}')}",
                )

            def round_values(val):
                try:
                    if float(val) < 5:
                        # round to three decimal places
                        return float(f"{float(val):.3f}")
                    elif 5 <= float(val) < 15:
                        # round to two decimal places
                        return float(f"{float(val):.2f}")
                    else:
                        return int(val)  # no decimal places
                except Exception as e:
                    print(f"\033[31m {e}\033[0m")

            print("{:<20} {:>15} {:>20}".format("Sensor", self.basename, other.basename))
            if isinstance(other, Log):
                df_stats1 = self.stats
                for k, v in df_stats1.items():
                    try:
                        num1, num2 = compare_values(round_values(v), round_values(other.stats[k]))
                        print(f"{k:<32} {num1:<15} {num2:>20}")
                    except KeyError:
                        pass

        def save(self):
            """
            Save the (updated) content to the log file (overwrites original content).
            """
            with open(self.path, "w") as f:
                f.write(self._content)
