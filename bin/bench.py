#!/usr/bin/python

import os
import errno
import subprocess as subp

def run(cmd):
    print(">>> " + str(cmd))
    process = subp.Popen(cmd)#, stdout=subp.PIPE, stderr=subp.PIPE)
    result = process.communicate()
    if process.returncode != 0:
        print '>>> non-zero return code ' + str(process.returncode)
    return process.returncode == 0

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def link(bench, conf):
    with open('project/plugins.sbt', 'w') as f:
        version = conf[0].split('-')[0]
        f.write('addSbtPlugin("org.scala-native" % "sbt-scala-native" % "{}")'.format(version))
    command = [sbt, 'clean']
    command.append('set nativeBenchmark := "{}"'.format(bench))
    command.extend(conf[1:])
    command.append('nativeLink')
    return run(command)

def compile(bench):
    command = [sbt, 'clean']
    command.append('set nativeBenchmark := "{}"'.format(bench))
    command.append('compile')
    return run(command)

def mode(n):
    return 'set nativeMode := "{}"'.format(n)

def gc(n):
    return 'set nativeGC := "{}"'.format(n)

configurations = [
        # ['version-label', setting1, setting2, ...]
        ['0.3.3-release-none', mode('release'), gc('none')],
        ['0.3.3-release-boehm', mode('release'), gc('boehm')],
        ['0.3.3-release-immix', mode('release'), gc('immix')],
]

benchmarks = [
        'bounce',
        'brainfuck',
        'cd',
        'deltablue',
        'json',
        'kmeans',
        'list',
        'permute',
        'richards',
        'sudoku',
]

runs = int(os.environ['BENCH_RUNS'])

iterations = int(os.environ['BENCH_ITER'])

sbt = os.environ['BENCH_SBT']

if __name__ == "__main__":
    for bench in benchmarks:
        for conf in configurations:
            mkdir_p('results/{}/{}/'.format(bench, conf[0]))
            link(bench, conf)
            for runid in xrange(runs):
                outfile = 'results/{}/{}/{}.data'.format(bench, conf[0], runid)
                run(['target/scala-2.11/benchmarks-out', str(iterations), outfile])
