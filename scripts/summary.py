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
                    points.append(float(line) / 1000000)
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


def bar_chart_relative(plt, percentile):
    ind = np.arange(len(benchmarks))
    conf_count = len(configurations) + 1
    base = []
    ref = []
    for bench in benchmarks:
        try:
            base.append(np.percentile(config_data(bench, configurations[0]), percentile))
            ref.append(1.0)
        except IndexError:
            base.append(0)
            ref.append(0.0)
    plt.bar(ind * conf_count, ref, label=configurations[0])

    for i, conf in enumerate(configurations[1:]):
        res = []
        for bench, base_val in zip(benchmarks, base):
            try:
                res.append(np.percentile(config_data(bench, conf), percentile) / base_val)
            except IndexError:
                res.append(0)
        plt.bar(ind * conf_count + i + 1, res, label=conf)
    plt.xticks((ind * conf_count + (conf_count - 1) / 2.0), map(benchmark_short_name, benchmarks))
    plt.title("Relative test execution times against " + configurations[0] + " at " + str(percentile) + " percentile")
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
    plt.ylim(ymin=0)
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
    header = ['name']
    header.append(configurations[0])
    for conf in configurations[1:]:
        header.append(conf)
        header.append("")
    file.write('|')
    file.write(' | '.join(header))
    file.write('|\n')

    file.write('|')
    for _ in header:
        file.write(' -- |')
    file.write('\n')

    for bench, res0 in zip(benchmarks, data):
        base = res0[0]
        res = [("%.4f" % base)] + sum(map(lambda x: cell(x, base), res0[1:]), [])
        file.write('|')
        file.write('|'.join([benchmark_md_link(bench)] + list(res)))
        file.write('|\n')


def cell(x, base):
    percent_diff = (float(x) / base - 1) * 100
    return [("%.4f" % x),
            ("+" if percent_diff > 0 else "__") + ("%.2f" % percent_diff) + "%" + ("" if percent_diff > 0 else "__")]


def benchmark_md_link(bench):
    return "[{}]({})".format(bench, bench.replace(".", "").lower())


def benchmark_short_name(bench):
    return bench.split(".")[0]


def write_md_file(rootdir, md_file):
    md_file.write("# Summary\n")
    for p in [50, 90, 99]:
        md_file.write("## Benchmark run time (s) at {} percentile \n".format(p))
        chart_name = "relative_percentile_" + str(p) + ".png"
        bar_chart_relative(plt, p).savefig(rootdir + chart_name)
        plt.clf()
        plt.cla()

        md_file.write("![Chart]({})\n\n".format(chart_name))

        write_md_table(md_file, percentile(p))

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


if __name__ == '__main__':
    if len(sys.argv) > 1:
        configurations = sys.argv[1:]
    # print_table(percentile(50))
    plt.rcParams["figure.figsize"] = [16.0, 12.0]
    rootdir = "reports/summary_" + time.strftime('%Y%m%d_%H%M%S') + "_" + "_vs_".join(configurations) + "/"
    mkdir(rootdir)
    with open(os.path.join(rootdir, "Readme.md"), 'w+') as md_file:
        write_md_file(rootdir, md_file)
