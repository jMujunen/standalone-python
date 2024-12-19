import cProfile
import io
import pstats


class FuncProfiler:
    """Function decorator for profiling code using cProfile.

    ### Example:
    ------------
    >>> @fProfiler(output_file="profile_stats.txt")
        def my_method():
            return
        my_method()

    """

    def __init__(self, output_file=None):
        self.profiler = cProfile.Profile()
        self.output_file = output_file

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            self.profiler.enable()
            result = func(*args, **kwargs)
            self.profiler.disable()
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
