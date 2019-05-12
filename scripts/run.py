#!/usr/bin/env python
import sys
import os
import errno
import subprocess as subp
import shutil as sh
import time
import argparse

def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
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
    start = time.time_ns()
    cmd = [sbt, '-J-Xmx6G', 'clean']
    cmd.append('set mainClass in Compile := Some("{}")'.format(bench))
    cmd.append(compilecmd)
    run(cmd)
    end = time.time_ns()
    return end - start

sbt = where('sbt')

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

confs_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + "/confs"

all_configs = next(os.walk(confs_path))[1]

if 'GRAALVM_HOME' in os.environ:
    all_configs += [
            'native-image',
            'native-image-pgo',
    ]

runs = 20
batches = 2000
batch_size = 1


def expand_wild_cards(arg):
    if arg == None:
        return arg
    elif arg.startswith("latest"):
        return latest + arg[len("latest"):]
    elif arg.startswith("stable"):
        return stable + arg[len("stable"):]
    else:
        return arg


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("set", nargs='*', default=[None])
    args = parser.parse_args()
    print args

    configurations = []
    for choice in args.set:
        expanded = expand_wild_cards(choice)
        if expanded == None:
            configurations = [stable, latest]
        else:
            configurations += [expanded]

    print "configurations:", configurations

    for conf in configurations:
        for bench in benchmarks:
            print('--- conf: {}, bench: {}'.format(conf, bench))

            resultsdir = os.path.join('results', conf, bench)
            mkdir(resultsdir)

            bindir = os.path.join("binaries", conf, bench)
            mkdir(bindir)

            binfile = os.path.join(bindir, bench)

            input = slurp(os.path.join('input', bench))
            output = slurp(os.path.join('output', bench))
            compilecmd = slurp(os.path.join('confs', conf, 'compile'))
            runcmd = slurp(os.path.join('confs', conf, 'run')).replace('$BENCH', bench).replace('$HOME', os.environ['HOME']).split(' ')

            if not os.path.exists(binfile):
                if os.path.exists(os.path.join('confs', conf, 'build.sbt')):
                    sh.copyfile(os.path.join('confs', conf, 'build.sbt'), 'build.sbt')
                else:
                    os.remove('build.sbt')

                if os.path.exists(os.path.join('confs', conf, 'build.properties')):
                    sh.copyfile(os.path.join('confs', conf, 'build.properties'), 'project/build.properties')
                else:
                    os.remove('project/build.properties')

                if os.path.exists(os.path.join('confs', conf, 'plugins.sbt')):
                    sh.copyfile(os.path.join('confs', conf, 'plugins.sbt'), 'project/plugins.sbt')
                else:
                    os.remove('project/plugins.sbt')

                compile_time = compile(bench, compilecmd)

                with open(os.path.join(resultsdir, "compile_time"), 'w') as f:
                    f.write(str(compile_time))

                sh.move(runcmd[0], binfile)

            for n in range(runs):
                print('--- run {}/{}'.format(n, runs))

                cmd = [binfile]
                cmd.extend(runcmd[1:])
                cmd.extend([str(batches), str(batch_size), input, output])
                out = run(cmd)
                with open(os.path.join(resultsdir, str(n)), 'wb') as resultfile:
                    resultfile.write(out)

