#!/usr/bin/env python2
from run import benchmarks, runs, configurations, mkdir

import numpy as np
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
            points = points[-1000:]
            # filter out 1% worst measurements as outliers
            pmax = np.percentile(points, 99)
            for point in points:
                if point <= pmax:
                    out.append(point)
        except IOError:
            pass
    return np.array(out)


def hot_config_data(bench, conf):
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


def peak_performance(percentile):
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
        data = hot_config_data(bench, conf)
        percentiles = np.arange(0, limit)
        percvalue = np.array([np.percentile(data, perc) for perc in percentiles])
        plt.plot(percentiles, percvalue, label = conf)
    plt.legend()
    plt.title(bench)
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
    print_table(peak_performance(50))
    # bar_chart(plt, 50).show()
    mkdir("reports")
    for bench in benchmarks:
        percentiles_chart(plt, bench).savefig("reports/percentile_" + bench + ".png")
        plt.clf()
        plt.cla()
