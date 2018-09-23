#!/usr/bin/env python2
from run import benchmarks, runs, configurations, mkdir

import numpy as np
import time
import sys
import matplotlib
import matplotlib.pyplot as plt
import os


def config_data(bench, conf):
    out = []
    for run in xrange(runs):
        try:
            points = []
            with open('results/{}/{}/{}'.format(conf, bench, run)) as data:
                for line in data.readlines():
                    points.append(float(line))
            # take only last 1000 to account for startup
            out += points[-1000:]
        except IOError:
            pass
    return np.array(out)


def percentile(percentile):
    out = []
    for bench in benchmarks:
        res = []
        for conf in configurations:
            try:
                res.append(np.percentile(config_data(bench, conf), percentile))
            except IndexError:
                res.append(0)
        out.append(res)
    return out


# not good
def bar_chart(plt, percentile):
    ind = np.arange(len(benchmarks))
    for conf in configurations:
        res = []
        for bench in benchmarks:
            try:
                res.append(np.percentile(config_data(bench, conf), percentile))
            except IndexError:
                res.append(0)
        plt.bar(ind, res, align='center', label=conf)
    plt.xticks(ind, map(benchmark_short_name, benchmarks))
    plt.legend()
    return plt


def percentiles_chart(plt, bench, limit=99):
    for conf in configurations:
        data = config_data(bench, conf)
        percentiles = np.arange(0, limit)
        percvalue = np.array([np.percentile(data, perc) for perc in percentiles])
        plt.plot(percentiles, percvalue, label=conf)
    plt.legend()
    plt.title(bench)
    plt.xlabel("Percentile")
    plt.ylabel("Run time (s)")
    return plt


def print_table(data):
    leading = ['name']
    for conf in configurations:
        leading.append(conf)
    print ','.join(leading)
    for bench, res in zip(benchmarks, data):
        print ','.join([bench] + list(map(str, res)))


def write_md_table(file, data):
    leading = ['name']
    for conf in configurations:
        leading.append(conf)
    file.write('|')
    file.write(' | '.join(leading))
    file.write('|\n')

    file.write('|')
    for _ in leading:
        file.write(' -- |')
    file.write('\n')

    for bench, res in zip(benchmarks, data):
        file.write('|')
        file.write('|'.join([bench] + list(map(str, res))))
        file.write('|\n')


def benchmark_short_name(bench):
    return bench.split(".")[0]


if __name__ == '__main__':
    if len(sys.argv) > 1:
        configurations = sys.argv[1:]
    print_table(percentile(50))
    # bar_chart(plt, 50).show()
    rootdir = "reports/summary_" + time.strftime('%Y%m%d_%H%M%S') + "_" + "_vs_".join(configurations) + "/"
    mkdir(rootdir)
    with open(os.path.join(rootdir, "Readme.md"), 'w+') as md_file:
        md_file.write("# Summary\n")
        md_file.write("## Benchmark run time (s) at 50 percentile \n")
        write_md_table(md_file, percentile(50))
        md_file.write("## Benchmark run time (s) at 90 percentile \n")
        write_md_table(md_file, percentile(90))
        md_file.write("## Benchmark run time (s) at 99 percentile \n")
        write_md_table(md_file, percentile(99))

        md_file.write("# Individual benchmarks\n")
        for bench in benchmarks:
            md_file.write("## ")
            md_file.write(bench)
            md_file.write("\n")

            chart_name = "percentile_" + bench + ".png"
            chart_file = rootdir + chart_name
            percentiles_chart(plt, bench).savefig(chart_file)
            plt.clf()
            plt.cla()

            md_file.write("![Chart]({})\n".format(chart_name))