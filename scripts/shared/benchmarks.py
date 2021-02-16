import os

from shared.file_utils import sbt, run, slurp, mkdir
import time
import subprocess
import sys

benchmarks = [
    'bounce.BounceBenchmark',
    'list.ListBenchmark',
    'queens.QueensBenchmark',
    'richards.RichardsBenchmark',
    'permute.PermuteBenchmark',
    'deltablue.DeltaBlueBenchmark',
    'tracer.TracerBenchmark',
    'json.JsonBenchmark',
    'sudoku.SudokuBenchmark',
    'brainfuck.BrainfuckBenchmark',
    'cd.CDBenchmark',
    'kmeans.KmeansBenchmark',
    'nbody.NbodyBenchmark',
    'rsc.RscBenchmark',
    'gcbench.GCBenchBenchmark',
    'mandelbrot.MandelbrotBenchmark',
    'histogram.Histogram'
]


class Benchmark:

    def __init__(self, name):
        self.name = name
        self.short_name = name.split(".")[0]

    def compile(self, conf):
        cmd = [sbt, '-J-Xmx6G', 'clean',
               'set mainClass in Compile := Some("{}")'.format(self.name),
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
        cmd.extend([str(conf.batches), str(conf.batch_size), input, output])
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
