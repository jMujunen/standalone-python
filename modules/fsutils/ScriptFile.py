from ExecutionTimer import ExecutionTimer

with ExecutionTimer():
    print('Script')
    from fsutils.GenericFile import File

    class Exe(File):
        """
        A class representing information about an executable file

        Attributes:
        ----------
            path (str): The absolute path to the file. (Required)

        Properties:
        ----------
            shebang (str): Return the shebang line of the file
            shebang.setter (str): Set a new shebang
        """

        def __init__(self, path):
            self._shebang = None
            super().__init__(path)

        @property
        def shebang(self):
            """
            Get the shebang line of the file.

            Returns:
            ----------
                str: The shebang line of the file
            """
            if self._shebang is None:
                self._shebang = self.head(1).strip()
            return self._shebang

        @shebang.setter
        def shebang(self, shebang):
            """
            Set a new shebang line for the file.

            Paramaters:
            ----------
                shebang (str): The new shebang line

            Returns:
            ----------
                str: The content of the file after updating the shebang line
            """
            self._content = shebang + self.read()[len(self.shebang.strip()) :]
            try:
                with open(self.path, "w", encoding="utf-8") as f:
                    f.seek(0)
                    f.write(self._content)

                print(f"{self.basename}\n{self.shebang} -> {shebang}")
                print(self.tail(2))
                self._shebang = shebang
                return self._content
            except PermissionError:
                print(f"Permission denied: {self.path}")
                pass
