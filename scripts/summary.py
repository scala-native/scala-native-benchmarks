#!/usr/bin/env python2
from run import benchmarks, mkdir, expand_wild_cards, generate_choices

import numpy as np
import time
import sys
import matplotlib
import matplotlib.pyplot as plt
import os
import argparse


def config_data(bench, conf):
    files = next(os.walk("results/{}/{}".format(conf, bench)), [[],[],[]])[2]
    runs = []
    for file in files:
        if "." not in file:
            # regular benchmark data
            runs += [file]

    out = []
    for run in runs:
        try:
            points = []
            with open('results/{}/{}/{}'.format(conf, bench, run)) as data:
                for line in data.readlines():
                    #in ms
                    points.append(float(line) / 1000000)
            # take only last 1000 to account for startup
            out += points[-1000:]
        except IOError:
            pass
    return np.array(out)

def gc_stats(bench, conf):
    files = next(os.walk("results/{}/{}".format(conf, bench)), [[],[],[]])[2]
    runs = []
    for file in files:
        if file.endswith(".gc.csv"):
            # gc stats data
            runs += [file]

    timestamps = [], mark_times = [], sweep_times = [], gc_times = []
    for run in runs:
        try:
            with open('results/{}/{}/{}'.format(conf, bench, run)) as data:
                #skip header
                #timestamp_us,collection,mark_time_us,sweep_time_us
                data.readline()
                for line in data.readlines():
                    arr = line.split(",")
                    timestamps.append(int(arr[0]))
                    # collection = arr[1]
                    # in ms
                    mark_time = float(arr[2])/ 1000
                    mark_times.append(mark_time)
                    sweep_time = float(arr[3])/ 1000
                    sweep_times.append(sweep_time)
                    gc_times.append(mark_time + sweep_time)
        except IOError:
            pass
    return np.array(timestamps), np.array(mark_times), np.array(sweep_times), np.array(gc_times)



def percentile(configurations, percentile):
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


def bar_chart_relative(plt, configurations, percentile):
    plt.clf()
    plt.cla()
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


def example_run_plot(plt, configurations, bench, run=3):
    plt.clf()
    plt.cla()

    for conf in configurations:
        points = []
        try:
            with open('results/{}/{}/{}'.format(conf, bench, run)) as data:
                for line in data.readlines():
                    points.append(float(line) / 1000000)
        except IOError:
            pass
        ind = np.arange(len(points))
        plt.plot(ind, points, label=conf)
    plt.title("{} run #{}".format(bench, str(run)))
    plt.xlabel("Iteration")
    plt.ylabel("Run time (ms)")
    plt.legend()
    return plt


def percentiles_chart(plt, configurations, bench, limit=99):
    plt.clf()
    plt.cla()
    for conf in configurations:
        data = config_data(bench, conf)
        if data.size > 0:
            percentiles = np.arange(0, limit)
            percvalue = np.array([np.percentile(data, perc) for perc in percentiles])
            plt.plot(percentiles, percvalue, label=conf)
    plt.legend()
    plt.title(bench)
    plt.ylim(ymin=0)
    plt.xlabel("Percentile")
    plt.ylabel("Run time (ms)")
    return plt


def print_table(configurations, data):
    leading = ['name']
    for conf in configurations:
        leading.append(conf)
    print ','.join(leading)
    for bench, res in zip(benchmarks, data):
        print ','.join([bench] + list(map(str, res)))


def write_md_table(file, configurations, data):
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
    return "[{}](#{})".format(bench, bench.replace(".", "").lower())


def benchmark_short_name(bench):
    return bench.split(".")[0]


def write_md_file(rootdir, md_file, configurations):
    md_file.write("# Summary\n")
    for p in [50, 90, 99]:
        md_file.write("## Benchmark run time (ms) at {} percentile \n".format(p))
        chart_name = "relative_percentile_" + str(p) + ".png"
        bar_chart_relative(plt, configurations, p).savefig(rootdir + chart_name)

        md_file.write("![Chart]({})\n\n".format(chart_name))

        write_md_table(md_file, configurations, percentile(configurations, p))

    md_file.write("# Individual benchmarks\n")
    for bench in benchmarks:
        md_file.write("## ")
        md_file.write(bench)
        md_file.write("\n")

        chart_name = "percentile_" + bench + ".png"
        chart_file = rootdir + chart_name
        percentiles_chart(plt, configurations, bench).savefig(chart_file)

        md_file.write("![Chart]({})\n".format(chart_name))

        chart_name = "example_run_3_" + bench + ".png"
        chart_file = rootdir + chart_name
        example_run_plot(plt, configurations, bench).savefig(chart_file)
        md_file.write("![Chart]({})\n".format(chart_name))


if __name__ == '__main__':
    all_configs = next(os.walk("results"))[1]
    results = generate_choices(all_configs)

    parser = argparse.ArgumentParser()
    parser.add_argument("--comment", help="comment at the suffix of the report name")
    parser.add_argument("comparisons", nargs='*', choices=results + ["all"],
                        default="all")
    args = parser.parse_args()

    configurations = []
    if args.comparisons == "all":
        configurations = all_configs
    else:
        for arg in args.comparisons:
            configurations += [expand_wild_cards(arg)]

    comment = "_vs_".join(configurations)
    if args.comment is not None:
        comment = args.comment

    report_dir = "reports/summary_" + time.strftime('%Y%m%d_%H%M%S') + "_" + comment + "/"
    plt.rcParams["figure.figsize"] = [16.0, 12.0]
    mkdir(report_dir)
    with open(os.path.join(report_dir, "Readme.md"), 'w+') as md_file:
        write_md_file(report_dir, md_file, configurations)

    print report_dir
