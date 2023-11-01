import os

from shared.file_utils import sbt, run, slurp, mkdir
import time
import subprocess
import sys

multiplier = 1
# Iterations of each benchmark taking ~1 second
benchmarks = [
    ('bounce.BounceBenchmark', 42000 * multiplier),
    ('brainfuck.BrainfuckBenchmark', 500 * multiplier),
    ('cd.CDBenchmark', 50 * multiplier),
    ('deltablue.DeltaBlueBenchmark', 9000 * multiplier),
    ('gcbench.GCBenchBenchmark', 10 * multiplier),
    ('histogram.Histogram', 650 * multiplier),
    ('json.JsonBenchmark', 960 * multiplier),
    ('kmeans.KmeansBenchmark', 20 * multiplier),
    ('list.ListBenchmark', 18400 * multiplier),
    ('mandelbrot.MandelbrotBenchmark', 10 * multiplier),
    ('nbody.NbodyBenchmark', 20 * multiplier),
    ('permute.PermuteBenchmark', 8000 * multiplier),
    ('queens.QueensBenchmark', 23000 * multiplier),
    ('richards.RichardsBenchmark', 19000 * multiplier),
    ('rsc.RscBenchmark', 45 * multiplier),
    ('sudoku.SudokuBenchmark', 880 * multiplier),
    ('tracer.TracerBenchmark', 2500 * multiplier)
]

class Benchmark:

    def __init__(self, name, batches):
        self.name = name
        self.batches = batches
        self.short_name = name.split(".")[0]

    def compile(self, conf):
        cmd = [sbt, '-J-Xmx6G', 'clean',
               'set Compile / mainClass := Some("{}")'.format(self.name),
               conf.compile_cmd()]
        start = time.time_ns()
        subprocess.run(cmd, stdout=sys.stdout, stderr=subprocess.STDOUT)
        end = time.time_ns()
        return end - start

    def run(self, conf):
        run_cmd = conf.run_cmd(self)
        input = slurp(os.path.join('input', self.name))
        output = slurp(os.path.join('output', self.name))
        cmd = []
        cmd.extend(run_cmd)
        cmd.extend([str(self.batches), str(conf.batch_size), input, output])
        return run(cmd)

    def ensure_results_dir(self, conf):
        dir = os.path.join(conf.ensure_results_dir(), self.name)
        mkdir(dir)
        return dir

    def results_dir(self, conf):
        return os.path.join(conf.results_dir, self.name)

    def __eq__(self, other):
        if isinstance(other, Benchmark):
            return self.name == other.name
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Benchmark(\'{}\')'.format(self.name)
