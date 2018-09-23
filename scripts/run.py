#!/usr/bin/env python2
import sys
import os
import errno
import subprocess as subp
import shutil as sh
import argparse


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def slurp(path):
    with open(path) as f:
        return f.read().strip()


def where(cmd):
    if os.path.isfile(cmd):
        return cmd
    else:
        paths = os.environ['PATH'].split(os.pathsep)
        for p in paths:
            f = os.path.join(p, cmd)
            if os.path.isfile(f):
                return f
        else:
            return None


def run(cmd):
    print(">>> " + str(cmd))
    return subp.check_output(cmd)


def compile(bench, compilecmd):
    cmd = [sbt, '-J-Xmx2G', 'clean']
    cmd.append('set mainClass in Compile := Some("{}")'.format(bench))
    cmd.append(compilecmd)
    return run(cmd)


sbt = where('sbt')

benchmarks = [
    'bounce.BounceBenchmark',
    'list.ListBenchmark',
    'richards.RichardsBenchmark',
    'queens.QueensBenchmark',
    'permute.PermuteBenchmark',
    'deltablue.DeltaBlueBenchmark',
    'tracer.TracerBenchmark',
    'brainfuck.BrainfuckBenchmark',
    'json.JsonBenchmark',
    'cd.CDBenchmark',
    'kmeans.KmeansBenchmark',
    'gcbench.GCBenchBenchmark',
    'mandelbrot.MandelbrotBenchmark',
    'nbody.NbodyBenchmark',
    'sudoku.SudokuBenchmark',
]

stable = 'scala-native-0.3.8'
baseline = [
    'jvm',
    stable,
]

latest = 'scala-native-0.3.9-SNAPSHOT'

configurations = all_configs = baseline + [latest]

if 'GRAALVM_HOME' in os.environ:
    baseline += [
        'native-image',
        'native-image-pgo',
    ]

runs = 20
batches = 3000
batch_size = 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--suffix", help="suffix added to results")
    parser.add_argument("set", nargs='*', choices=configurations + ["baseline", "latest", "stable", "all"],
                        default="all")
    args = parser.parse_args()

    if args.set != all_configs:
        configurations = []
        for choice in args.set:
            if choice == "baseline":
                configurations += baseline
            elif choice == "latest" in args.set:
                configurations += [latest]
            elif choice == "stable" in args.set:
                configurations += [stable]
            else:
                configurations + [choice]
    else:
        configurations = all_configs

    for conf in configurations:
        for bench in benchmarks:
            print('--- conf: {}, bench: {}'.format(conf, bench))

            input = slurp(os.path.join('input', bench))
            output = slurp(os.path.join('output', bench))
            compilecmd = slurp(os.path.join('confs', conf, 'compile'))
            runcmd = slurp(os.path.join('confs', conf, 'run')).replace('$BENCH', bench).replace('$HOME', os.environ[
                'HOME']).split(' ')

            if os.path.exists(os.path.join('confs', conf, 'build.sbt')):
                sh.copyfile(os.path.join('confs', conf, 'build.sbt'), 'build.sbt')
            else:
                os.remove('build.sbt')

            if os.path.exists(os.path.join('confs', conf, 'plugins.sbt')):
                sh.copyfile(os.path.join('confs', conf, 'plugins.sbt'), 'project/plugins.sbt')
            else:
                os.remove('project/plugins.sbt')

            compile(bench, compilecmd)
            resultsdir = os.path.join('results', conf + "_" + args.suffix, bench)
            mkdir(resultsdir)

            for n in xrange(runs):
                print('--- run {}/{}'.format(n, runs))

                cmd = []
                cmd.extend(runcmd)
                cmd.extend([str(batches), str(batch_size), input, output])
                out = run(cmd)
                with open(os.path.join(resultsdir, str(n)), 'w+') as resultfile:
                    resultfile.write(out)
