import os

from shared.file_utils import sbt, run, slurp, mkdir
import time
import subprocess
import sys

benchmarks = [
    ('bounce.BounceBenchmark',50000),
    ('list.ListBenchmark',50000),
    ('richards.RichardsBenchmark',50000),
    ('queens.QueensBenchmark',50000),
    ('deltablue.DeltaBlueBenchmark',20000),
    ('tracer.TracerBenchmark',20000),
    ('json.JsonBenchmark',20000),
    ('permute.PermuteBenchmark',10000),
    ('brainfuck.BrainfuckBenchmark',10000),
    ('sudoku.SudokuBenchmark',10000),
    ('cd.CDBenchmark',1000),
    ('histogram.Histogram',1000),
    ('nbody.NbodyBenchmark',1000),
    ('rsc.RscBenchmark',1000),
    ('gcbench.GCBenchBenchmark',250),
    ('kmeans.KmeansBenchmark',250),
    ('mandelbrot.MandelbrotBenchmark', 250)
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
