import cProfile
import io
import pstats


class Profiler:
    """Class decorator for profiling code using cProfile."""

    def __init__(self, output_file=None):
        # Initialize the cProfile.Profile() object which will be used to profile our functions.
        self.profiler = cProfile.Profile()
        self.output_file = output_file

    def __call__(self, cls):
        original_init = cls.__init__

        def new_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            self.ttprofiler.enable()

        cls.__init__ = new_init

        for attr_name, attr_value in vars(cls).items():
            if callable(attr_value) and not isinstance(attr_value, staticmethod):
                setattr(cls, attr_name, self._profile_method(attr_value))

        return cls

    def _profile_method(self, func):
        def wrapper(*args, **kwargs):
            result = self.profiler.runcall(func, *args, **kwargs)
            sio = io.StringIO()
            stats = pstats.Stats(self.profiler, stream=sio).sort_stats("cumulative")
            stats.print_stats()
            print(sio.getvalue())

            if self.output_file:
                with open(self.output_file, "w") as f:
                    stats = pstats.Stats(self.profiler, stream=f).sort_stats("cumulative")
                    stats.print_stats()

            return result

        return wrapper


# ICONS : test

# TODO: Add this to docstring
if __name__ == "__main__":

    @Profiler(output_file="profile_stats.txt")
    class SomeClass:
        def method1(self):
            return

        def method2(self):
            return

    # Creating an instance of `SomeClass`, all methods will be profiled.
    my_instance = SomeClass()
