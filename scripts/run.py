#!/usr/bin/env python
import argparse
import os

from shared.benchmarks import Benchmark
from shared.configurations import Configuration

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
    'histogram.Histogram',
]

stable = 'scala-native-0.4.0'
latest = 'scala-native-0.4.1-SNAPSHOT'


def expand_wild_cards(arg):
    if arg is None:
        return arg
    elif arg.startswith("latest"):
        return latest + arg[len("latest"):]
    elif arg.startswith("stable"):
        return stable + arg[len("stable"):]
    else:
        return arg


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="interactive mode", action="store_true")
    parser.add_argument("set", nargs='*', default=[None])
    args = parser.parse_args()
    print args

    if args.i:
        from IPython import embed
        embed()
    else:
        configurations = []
        for choice in args.set:
            expanded = expand_wild_cards(choice)
            if expanded is None:
                configurations = [stable, latest]
            else:
                configurations += [expanded]

        print "configurations:", configurations

        for conf_name in configurations:
            conf = Configuration(conf_name)
            conf.make_active()
            for bench_name in benchmarks:
                bench = Benchmark(bench_name)
                print('--- conf: {}, bench: {}'.format(conf, bench))

                bench.compile(conf)
                resultsdir = bench.ensure_results_dir(conf)

                runs = conf.runs
                for n in xrange(runs):
                    print('--- run {}/{}'.format(n, runs))

                    out = bench.run(conf)
                    with open(os.path.join(resultsdir, str(n)), 'wb') as resultfile:
                        resultfile.write(out)
