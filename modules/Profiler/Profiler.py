import cProfile
import io
import pstats


class Profiler:
    """Context manager for profiling code using cProfile."""

    def __init__(self, output_file=None):
        self.profiler = cProfile.Profile()
        self.output_file = output_file

    def __enter__(self):
        self.profiler.enable()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.profiler.disable()
        sio = io.StringIO()
        stats = pstats.Stats(self.profiler, stream=sio).sort_stats("cumulative")
        stats.print_stats()
        print(sio.getvalue())

        if self.output_file:
            with open(self.output_file, "w") as f:
                stats = pstats.Stats(self.profiler, stream=f).sort_stats("cumulative")
                stats.print_stats()
