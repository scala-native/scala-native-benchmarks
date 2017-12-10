#!/usr/bin/python

import os
import errno
import subprocess as subp

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
    process = subp.Popen(cmd)
    result = process.communicate()
    if process.returncode != 0:
        print '>>> non-zero return code ' + str(process.returncode)
    return process.returncode == 0

def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def link(bench, conf):
    sbt = where('sbt')
    command = ['sbt', 'clean']
    command.append('set nativeBenchmark := "{}"'.format(bench))
    command.extend(settings(conf))
    command.append('nativeLink')
    return run(command)

def settings(conf):
    out = []
    for key, value in conf.iteritems():
        if key == 'name':
            pass
        elif key == 'native':
            with open('project/plugins.sbt', 'w') as f:
                f.write('addSbtPlugin("org.scala-native" % "sbt-scala-native" % "{}")'.format(value))
        elif key == 'clang':
            clang = where('clang-{}'.format(value))
            clangpp = where('clang++-{}'.format(value))
            out.append('set nativeClang := file("{}")'.format(clang))
            out.append('set nativeClangPP := file("{}")'.format(clangpp))
        elif key == 'scala':
            out.append('set scalaVersion := "{}"'.format(value))
        elif key == 'mode':
            out.append('set nativeMode := "{}"'.format(value))
        elif key == 'gc':
            out.append('set nativeGC := "{}"'.format(value))
        else:
            raise Exception('Unkown configuration key: ' + key)
    return out

def conf(**kwargs):
    return kwargs

configurations = [
        conf(name='0.3.3-immix', native='0.3.3', clang='5.0', scala='2.11.11', mode='release', gc='immix'),
        conf(name='0.3.4-immix', native='0.3.4', clang='5.0', scala='2.11.11', mode='release', gc='immix'),
]

benchmarks = [
        'bounce',
        'brainfuck',
        'cd',
        'deltablue',
        'gcbench',
        'json',
        'kmeans',
        'list',
        'mandelbrot',
        'nbody',
        'permute',
        'queens',
        'richards',
        'sudoku',
        'tracer',
]

runs = 50

iterations = 1000

if __name__ == "__main__":
    for bench in benchmarks:
        for conf in configurations:
            mkdir('results/{}/{}/'.format(bench, conf['name']))
            link(bench, conf)
            for runid in xrange(runs):
                outfile = 'results/{}/{}/{}.data'.format(bench, conf['name'], runid)
                run(['target/scala-2.11/benchmarks-out', str(iterations), outfile])
