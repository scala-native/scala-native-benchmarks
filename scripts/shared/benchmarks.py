import os

from file_utils import sbt, run, slurp, mkdir

all_benchmarks = [
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
]


class Benchmark:

    def __init__(self, name):
        self.name = name

    def compile(self, conf):
        cmd = [sbt, '-J-Xmx6G', 'clean']
        cmd.append('set mainClass in Compile := Some("{}")'.format(self.name))
        cmd.append(conf.compile_cmd())
        return run(cmd)

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

    def __str__(self):
        return self.name
