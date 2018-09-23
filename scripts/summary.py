#!/usr/bin/env python2
from run import benchmarks, runs, configurations, mkdir

import numpy as np
import time
import matplotlib
import matplotlib.pyplot as plt


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
    plt.xlabel("Percentile (%)")
    plt.ylabel("Run time (s)")
    return plt


def print_table(data):
    leading = ['name']
    for conf in configurations:
        leading.append(conf)
    print ','.join(leading)
    for bench, res in zip(benchmarks, data):
        print ','.join([benchmark_short_name(bench)] + list(map(str, res)))


def benchmark_short_name(bench):
    return bench.split(".")[0]


if __name__ == '__main__':
    print_table(percentile(50))
    # bar_chart(plt, 50).show()
    rootdir = "reports/summary_" + time.strftime('%Y%m%d_%H%M%S') + "/"
    mkdir(rootdir)
    for bench in benchmarks:
        percentiles_chart(plt, bench).savefig(rootdir + "percentile_" + bench + ".png")
        plt.clf()
        plt.cla()
