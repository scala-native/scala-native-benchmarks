#!/usr/bin/env python2
from run import mkdir, expand_wild_cards, generate_choices

import numpy as np
import time
import matplotlib.pyplot as plt
import os
import argparse


def config_data(bench, conf):
    benchmark_dir = os.path.join("results", conf, bench)
    files = next(os.walk(benchmark_dir), [[], [], []])[2]
    runs = []
    for file in files:
        if "." not in file:
            # regular benchmark data
            runs.append(file)

    out = []
    for run in runs:
        try:
            points = []
            with open(os.path.join("results", conf, bench, run)) as data:
                for line in data.readlines():
                    # in ms
                    points.append(float(line) / 1000000)
            # take only last 1000 to account for startup
            out += points[-1000:]
        except IOError:
            pass
    return np.array(out)


def gc_stats(bench, conf):
    benchmark_dir = os.path.join("results", conf, bench)
    files = next(os.walk(benchmark_dir), [[], [], []])[2]
    runs = []
    for file in files:
        if file.endswith(".gc.csv"):
            # gc stats data
            runs.append(file)

    mark_times = []
    sweep_times = []
    gc_times = []
    for run in runs:
        try:
            file = os.path.join("results", conf, bench, run)
            with open(file) as data:
                mark, sweep, total = gc_parse_file(data, file)
                mark_times += mark
                sweep_times += sweep
            gc_times += total
        except IOError:
            pass
    return np.array(mark_times), np.array(sweep_times), np.array(gc_times)


def gc_parse_file(data, file):
    header = data.readline().strip()
    if header.startswith("event_type,"):
        return parse_gc_events(data, file, header)
    else:
        return parse_gc_tabular(data, file, header)


def parse_gc_events(data, file, header):
    mark_times = []
    sweep_times = []
    gc_times = []
    event_type_index = 0
    time_ns_index = -1
    ns_to_ms_div = 1000 * 1000
    for i, h in enumerate(header.split(',')):
        if h == "time_ns":
            time_ns_index = i
    if time_ns_index == -1:
        print "Header does not have time_ns", header, "at", file
        return mark_times, sweep_times, gc_times

    for line in data.readlines():
        arr = line.split(",")
        event = arr[event_type_index]
        time = float(arr[time_ns_index]) / ns_to_ms_div
        if event == "mark":
            mark_times.append(time)
        elif event == "sweep":
            sweep_times.append(time)
        gc_times.append(time)

    return mark_times, sweep_times, gc_times


def parse_gc_tabular(data, file, header):
    mark_times = []
    sweep_times = []
    gc_times = []
    # analise header
    mark_index = -1
    sweep_index = -1
    mark_to_ms = 0
    sweep_to_ms = 0
    unit2div = dict(ms=1, us=1000, ns=1000 * 1000)
    for i, h in enumerate(header.split(',')):
        arr = h.rsplit('_', 1)
        if len(arr) != 2:
            continue
        prefix = arr[0]
        unit = arr[1]

        if prefix == "mark_time":
            mark_index = i
            mark_to_ms = unit2div[unit]
        elif prefix == "sweep_time":
            sweep_index = i
            sweep_to_ms = unit2div[unit]
    if mark_index == -1:
        print "Header does not have mark_time_<unit>", header, "at", file
    if sweep_index == -1:
        print "Header does not have sweep_time_<unit>", header, "at", file
    if mark_index == -1 or sweep_index == -1:
        return mark_times, sweep_times, gc_times
    for line in data.readlines():
        arr = line.split(",")
        # in ms
        mark_time = float(arr[mark_index]) / mark_to_ms
        mark_times.append(mark_time)
        sweep_time = float(arr[sweep_index]) / sweep_to_ms
        sweep_times.append(sweep_time)
        gc_times.append(mark_time + sweep_time)
    return mark_times, sweep_times, gc_times


def gc_stats_total(bench, conf):
    _, _, total = gc_stats(bench, conf)
    return total



def percentile_gc(configurations, benchmarks, percentile):
    out_mark = []
    out_sweep = []
    out_total = []
    for bench in benchmarks:
        res_mark, res_sweep, res_total = percentile_gc_bench(configurations, bench, percentile)
        out_mark.append(res_mark)
        out_sweep.append(res_sweep)
        out_total.append(res_total)

    return out_mark, out_sweep, out_total

def total_gc(configurations, benchmarks):
    out_mark = []
    out_sweep = []
    out_total = []
    for bench in benchmarks:
        res_mark, res_sweep, res_total = total_gc_bench(configurations, bench)
        out_mark.append(res_mark)
        out_sweep.append(res_sweep)
        out_total.append(res_total)
    return out_mark, out_sweep, out_total



def percentile_gc_bench(configurations, bench, p):
    res_mark = []
    res_sweep = []
    res_total = []
    for conf in configurations:
        try:
            mark, sweep, total = gc_stats(bench, conf)
            res_mark.append(np.percentile(mark, p))
            res_sweep.append(np.percentile(sweep, p))
            res_total.append(np.percentile(total, p))
        except IndexError:
            res_mark.append(0)
            res_sweep.append(0)
            res_total.append(0)
    return res_mark, res_sweep, res_total


def total_gc_bench(configurations, bench):
    res_mark = []
    res_sweep = []
    res_total = []
    for conf in configurations:
        try:
            mark, sweep, total = gc_stats(bench, conf)
            res_mark.append(np.sum(mark))
            res_sweep.append(np.sum(sweep))
            res_total.append(np.sum(total))
        except IndexError:
            res_mark.append(0)
            res_sweep.append(0)
            res_total.append(0)
    return res_mark, res_sweep, res_total


def percentile_gc_bench_mark(configurations, bench, p):
    mark, _, _ = percentile_gc_bench(configurations, bench, p)
    return mark


def percentile_gc_bench_sweep(configurations, bench, p):
    _, sweep, _ = percentile_gc_bench(configurations, bench, p)
    return sweep


def percentile_gc_bench_total(configurations, bench, p):
    _, _, total = percentile_gc_bench(configurations, bench, p)
    return total


def percentile(configurations, benchmarks, p):
    out = []
    for bench in benchmarks:
        out.append(percentile_bench(configurations, bench, p))
    return out


def percentile_bench(configurations, bench, p):
    res = []
    for conf in configurations:
        try:
            res.append(np.percentile(config_data(bench, conf), p))
        except IndexError:
            res.append(0)
    return res


def totals(configurations, benchmarks):
    out = []
    for bench in benchmarks:
        out.append(totals_bench(configurations, bench))
    return out


def totals_bench(configurations, bench):
    res = []
    for conf in configurations:
        try:
            res.append(np.sum(config_data(bench, conf)))
        except IndexError:
            res.append(0)
    return res


def bar_chart_relative(plt, configurations, benchmarks, data):
    plt.clf()
    plt.cla()
    ind = np.arange(len(benchmarks))
    conf_count = len(configurations) + 1
    base = []
    ref = []
    for bench_idx, bench in enumerate(benchmarks):
        try:
            base_val = data[bench_idx][0]
            if base_val > 0:
                base.append(base_val)
                ref.append(1.0)
            else:
                base.append(0.0)
                ref.append(0.0)
        except IndexError:
            base.append(0.0)
            ref.append(0.0)
    plt.bar(ind * conf_count, ref, label=configurations[0])

    for i, conf in enumerate(configurations[1:]):
        conf_idx = i + 1
        res = []
        for bench_idx, (bench, base_val) in enumerate(zip(benchmarks, base)):
            try:
                if base_val > 0:
                    res.append(data[bench_idx][conf_idx] / base_val)
                else:
                    res.append(0.0)
            except IndexError:
                res.append(0)
        plt.bar(ind * conf_count + conf_idx, res, label=conf)
    plt.xticks((ind * conf_count + (conf_count - 1) / 2.0), map(benchmark_short_name, benchmarks))
    plt.legend()
    return plt


def total_execution_times(plt, configurations, benchmarks, data):
    plt = bar_chart_relative(plt, configurations, benchmarks, data)
    plt.title("Total test execution times against " + configurations[0])
    return plt


def relative_execution_times(plt, configurations, benchmarks, data, p):
    plt = bar_chart_relative(plt, configurations, benchmarks, data)
    plt.title("Relative test execution times against " + configurations[0] + " at " + str(p) + " percentile")
    return plt


def relative_gc_pauses(plt, configurations, benchmarks, data, p):
    plt = bar_chart_relative(plt, configurations, benchmarks, data)
    plt.title("Relative GC pauses against " + configurations[0] + " at " + str(p) + " percentile")
    return plt


def bar_chart_gc_relative(plt, configurations, benchmarks, mark_data, total_data):
    plt.clf()
    plt.cla()
    ind = np.arange(len(benchmarks))
    conf_count = len(configurations) + 1
    base = []
    ref = []
    mark_ref = []
    for bench_idx, bench in enumerate(benchmarks):
        mark = mark_data[bench_idx][0]
        total = total_data[bench_idx][0]
        if total > 0:
            base.append(total)
            ref.append(1.0)
            mark_ref.append(mark / total)
        else:
            base.append(0)
            ref.append(0.0)
            mark_ref.append(0.0)
    plt.bar(ind * conf_count, ref, label=configurations[0] + "-sweep")  # total (look like sweep)
    plt.bar(ind * conf_count, mark_ref, label=configurations[0] + "-mark")  # mark time

    for i, conf in enumerate(configurations[1:]):
        conf_idx = i + 1
        res = []
        mark_res = []
        for bench_idx, (bench, base_val) in enumerate(zip(benchmarks, base)):
            if base_val > 0:
                mark, _, total = gc_stats(bench, conf)
                mark = mark_data[bench_idx][conf_idx]
                total = total_data[bench_idx][conf_idx]
                res.append(np.array(total) / base_val)
                mark_res.append(np.array(mark) / base_val)
            else:
                res.append(0)
                mark_res.append(0)
        plt.bar(ind * conf_count + i + 1, res, label=conf + "-sweep")  # total (look like sweep)
        plt.bar(ind * conf_count + i + 1, mark_res, label=conf + "-mark")  # mark time
    plt.xticks((ind * conf_count + (conf_count - 1) / 2.0), map(benchmark_short_name, benchmarks))
    plt.title("Relative gc times against " + configurations[0])
    plt.legend()
    return plt


def bar_chart_gc_absolute(plt, configurations, benchmarks, percentile):
    plt.clf()
    plt.cla()
    ind = np.arange(len(benchmarks))
    conf_count = len(configurations) + 1

    for i, conf in enumerate(configurations):
        res = []
        mark_res = []
        for bench in benchmarks:
            try:
                mark, _, total = gc_stats(bench, conf)
                res.append(np.percentile(total, percentile))
                mark_res.append(np.percentile(mark, percentile))
            except IndexError:
                res.append(0)
        plt.bar(ind * conf_count + i + 1, res, label=conf + "-sweep")  # total (look like sweep)
        plt.bar(ind * conf_count + i + 1, mark_res, label=conf + "-mark")  # mark time
    plt.xticks((ind * conf_count + (conf_count - 1) / 2.0), map(benchmark_short_name, benchmarks))
    plt.title("Garbage collector pause times at " + str(percentile) + " percentile")
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


def to_gb(size_str):
    if size_str[-1] == "k" or size_str[-1] == "K":
        return float(size_str[:-1]) / 1024 / 1024
    elif size_str[-1] == "m" or size_str[-1] == "M":
        return float(size_str[:-1]) / 1024
    elif size_str[-1] == "g" or size_str[-1] == "G":
        return float(size_str[:-1])
    else:
        # bytes
        return float(size_str) / 1024 / 1024 / 1024


def sizes_per_conf(parent_configuration):
    parent_folder = os.path.join("results", parent_configuration)
    min_sizes = []
    max_sizes = []
    child_confs = []
    folders = next(os.walk(parent_folder))[1]
    for f in folders:
        if f.startswith("size_"):
            parts = f[len("size_"):].split("-")
            min_sizes.append(to_gb(parts[0]))
            max_sizes.append(to_gb(parts[1]))
            child_confs.append(os.path.join(parent_configuration,f))
    return min_sizes, max_sizes, child_confs


def size_compare_chart_generic(plt, parent_configurations, bench, get_percentile, p):
    plt.clf()
    plt.cla()
    for parent_conf in parent_configurations:
        min_sizes, max_sizes, child_confs = sizes_per_conf(parent_conf)
        equal_sizes = []
        equal_confs = []
        for min_size, max_size, child_conf in zip(min_sizes, max_sizes, child_confs):
            if min_size == max_size:
                equal_sizes.append(min_size)
                equal_confs.append(child_conf)

        # sorts all by size in GB
        equal_sizes, equal_confs  = zip(*[(x,y) for x,y in sorted(zip(equal_sizes,equal_confs))])
        percentiles = get_percentile(equal_confs, bench, p)
        plt.plot(np.array(equal_sizes), percentiles, label=parent_conf)
    plt.legend()
    plt.xlim(xmin=0)
    plt.ylim(ymin=0)
    plt.xlabel("Heap Size (GB)")

    return plt


def size_compare_chart_gc_combined(plt, parent_configurations, bench):
    plt.clf()
    plt.cla()
    for parent_conf in parent_configurations:
        min_sizes, max_sizes, child_confs = sizes_per_conf(parent_conf)
        equal_sizes = []
        equal_confs = []
        for min_size, max_size, child_conf in zip(min_sizes, max_sizes, child_confs):
            if min_size == max_size:
                equal_sizes.append(min_size)
                equal_confs.append(child_conf)

        # sorts all by size in GB
        equal_sizes, equal_confs  = zip(*[(x,y) for x,y in sorted(zip(equal_sizes,equal_confs))])

        mark, _, total = total_gc_bench(equal_confs, bench)
        plt.plot(np.array(equal_sizes), total, label=parent_conf + "-sweep") # total (look like sweep)
        plt.plot(np.array(equal_sizes), mark, label=parent_conf + "-mark") # mark time
    plt.legend()
    plt.xlim(xmin=0)
    plt.ylim(ymin=0)
    plt.xlabel("Heap Size (GB)")
    plt.title("{}: GC total time".format(bench))
    plt.ylabel("Time (ms)")

    return plt


def size_compare_chart(plt, parent_configurations, bench, p):
    plt = size_compare_chart_generic(plt, parent_configurations, bench, percentile_bench, p)
    plt.title("{} at {} percentile".format(bench, p))
    plt.ylabel("Run time (ms)")
    return  plt


def size_compare_chart_gc(plt, parent_configurations, bench, p):
    plt = size_compare_chart_generic(plt, parent_configurations, bench, percentile_gc_bench_total, p)
    plt.title("{}: GC pause time at {} percentile".format(bench, p))
    plt.ylabel("GC pause time (ms)")
    return plt


def size_compare_chart_gc_mark(plt, parent_configurations, bench, p):
    plt = size_compare_chart_generic(plt, parent_configurations, bench, percentile_gc_bench_mark, p)
    plt.title("{}: GC mark pause time at {} percentile".format(bench, p))
    plt.ylabel("GC mark time (ms)")
    return plt

def size_compare_chart_gc_sweep(plt, parent_configurations, bench, p):
    plt = size_compare_chart_generic(plt, parent_configurations, bench, percentile_gc_bench_sweep, p)
    plt.title("{}: GC sweep pause time at {} percentile".format(bench, p))
    plt.ylabel("GC sweep time (ms)")
    return plt


def percentiles_chart_generic(plt, configurations, bench, get_data, limit):
    plt.clf()
    plt.cla()
    for conf in configurations:
        data = get_data(bench, conf)
        if data.size > 0:
            percentiles = np.arange(0, limit)
            percvalue = np.array([np.percentile(data, perc) for perc in percentiles])
            plt.plot(percentiles, percvalue, label=conf)
    plt.legend()
    plt.ylim(ymin=0)
    plt.xlabel("Percentile")
    return plt


def percentiles_chart(plt, configurations, bench, limit=99):
    plt = percentiles_chart_generic(plt, configurations, bench, config_data, limit)
    plt.title(bench)
    plt.ylabel("Run time (ms)")
    return plt

def gc_pause_time_chart(plt, configurations, bench, limit=100):
    plt = percentiles_chart_generic(plt, configurations, bench, gc_stats_total, limit)
    plt.title(bench + ": Garbage Collector Pause Times")
    plt.ylabel("GC pause time (ms)")
    return plt

def print_table(configurations, benchmarks, data):
    leading = ['name']
    for conf in configurations:
        leading.append(conf)
    print ','.join(leading)
    for bench, res in zip(benchmarks, data):
        print ','.join([bench] + list(map(str, res)))


def write_md_table(file, configurations, benchmarks, data):
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

    gmul = np.ones(len(configurations) - 1)
    gcount = np.zeros(len(configurations) - 1)
    for bench, res0 in zip(benchmarks, data):
        base = res0[0]
        res = [("%.4f" % base)] + sum(map(lambda x: cell(x, base), res0[1:]), [])
        file.write('|')
        file.write('|'.join([benchmark_md_link(bench)] + list(res)))
        file.write('|\n')

        for i, d0 in enumerate(res0[1:]):
            if d0 != 0 and base != 0:
                gmul[i] *= (float(d0) / base)
                gcount[i] += 1

    file.write('| __Geometrical mean:__|')
    for gm, count in zip(gmul, gcount):
        file.write('| |')
        if count > 0:
            gmean = float(gm) ** (1.0 / count)
            percent_diff = (gmean - 1) * 100
            precent_diff_cell = ("+" if percent_diff > 0 else "__") + ("%.2f" % percent_diff) + "%" + (
                "" if percent_diff > 0 else "__")
            file.write(precent_diff_cell)
        else:
            file.write(" ")
    file.write("|\n")


def write_md_table_gc(file, configurations, benchmarks, mark_data, sweep_data, total_data):
    header = ['name', ""]
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

    mark_gmul = np.ones(len(configurations) - 1)
    mark_gcount = np.zeros(len(configurations) - 1)
    sweep_gmul = np.ones(len(configurations) - 1)
    sweep_gcount = np.zeros(len(configurations) - 1)
    total_gmul = np.ones(len(configurations) - 1)
    total_gcount = np.zeros(len(configurations) - 1)
    for bench, mark_res0, sweep_res0, total_res0 in zip(benchmarks, mark_data, sweep_data, total_data):
        for name, res0, gmul, gcount in zip(["mark", "sweep", "total"], [mark_res0, sweep_res0, total_res0],
                                            [mark_gmul, sweep_gmul, total_gmul],
                                            [mark_gcount, sweep_gcount, total_gcount]):
            base = res0[0]
            res = [("%.4f" % base)] + sum(map(lambda x: cell(x, base), res0[1:]), [])

            if name == "mark":
                link = [benchmark_md_link(bench)]
            else:
                link = [""]

            file.write('|')
            file.write('|'.join(link + list([name]) + list(res)))
            file.write('|\n')

            for i, d0 in enumerate(res0[1:]):
                if d0 != 0 and base != 0:
                    gmul[i] *= (float(d0) / base)
                    gcount[i] += 1

    for name, gmul, gcount in zip(["mark", "sweep", "total"],
                                  [mark_gmul, sweep_gmul, total_gmul],
                                  [mark_gcount, sweep_gcount, total_gcount]):
        if name == "mark":
            link = "__Geometrical mean:__"
        else:
            link = ""

        file.write('|' + link + '|' + name + '|')
        for gm, count in zip(gmul, gcount):
            file.write('| |')
            if count > 0:
                gmean = float(gm) ** (1.0 / count)
                percent_diff = (gmean - 1) * 100
                precent_diff_cell = ("+" if percent_diff > 0 else "__") + ("%.2f" % percent_diff) + "%" + (
                    "" if percent_diff > 0 else "__")
                file.write(precent_diff_cell)
            else:
                file.write(" ")
        file.write("|\n")




def cell(x, base):
    if base > 0:
        percent_diff = (float(x) / base - 1) * 100
        precent_diff_cell = ("+" if percent_diff > 0 else "__") + ("%.2f" % percent_diff) + "%" + (
            "" if percent_diff > 0 else "__")
    else:
        precent_diff_cell = "N/A"
    return [("%.4f" % x), precent_diff_cell]


def benchmark_md_link(bench):
    return "[{}](#{})".format(bench, bench.replace(".", "").lower())


def benchmark_short_name(bench):
    return bench.split(".")[0]


def chart_md(md_file, plt, rootdir, name):
    plt.savefig(rootdir + name)
    md_file.write("![Chart]({})\n\n".format(name))


def write_md_file(rootdir, md_file, parent_configurations, configurations, benchmarks, gc_charts=False, size_charts=False):
    interesting_percentiles = [50, 90, 99]
    md_file.write("# Summary\n")
    for p in interesting_percentiles:
        md_file.write("## Benchmark run time (ms) at {} percentile \n".format(p))
        data = percentile(configurations, benchmarks, p)
        chart_md(md_file, relative_execution_times(plt, configurations, benchmarks, data, p), rootdir,
                 "relative_percentile_" + str(p) + ".png")
        write_md_table(md_file, configurations, benchmarks, data)

    md_file.write("## Benchmark total run time (ms) \n")
    data = totals(configurations, benchmarks)
    chart_md(md_file, total_execution_times(plt, configurations, benchmarks, data), rootdir,
             "relative_total.png")
    write_md_table(md_file, configurations, benchmarks, data)

    if gc_charts:
        md_file.write("## Total GC time on Application thread (ms) \n")
        mark, sweep, total = total_gc(configurations, benchmarks)
        chart_md(md_file, bar_chart_gc_relative(plt, configurations, benchmarks, mark, total), rootdir,
                 "relative_gc_total.png")
        write_md_table_gc(md_file, configurations, benchmarks, mark, sweep, total)

        for p in interesting_percentiles:
            md_file.write("## GC pause time (ms) at {} percentile \n".format(p))
            _, _, total = percentile_gc(configurations, benchmarks, p)
            chart_md(md_file, relative_gc_pauses(plt, configurations, benchmarks, total, p), rootdir,
                     "relative_gc_percentile_" + str(p) + ".png")
            write_md_table(md_file, configurations, benchmarks, total)

    md_file.write("# Individual benchmarks\n")
    for bench in benchmarks:
        if not any_run_exists(bench, configurations, 0):
            continue

        md_file.write("## ")
        md_file.write(bench)
        md_file.write("\n")

        chart_md(md_file, percentiles_chart(plt, configurations, bench), rootdir, "percentile_" + bench + ".png")
        if gc_charts:
            chart_md(md_file, gc_pause_time_chart(plt, configurations, bench), rootdir,
                     "gc_pause_times_" + bench + ".png")
            if size_charts:
                for p in interesting_percentiles:
                    chart_md(md_file, size_compare_chart_gc_mark(plt, parent_configurations, bench, p), rootdir,
                             "gc_size_chart" + bench + "percentile_" + str(p) + "_mark.png")
                for p in interesting_percentiles:
                    chart_md(md_file, size_compare_chart_gc_sweep(plt, parent_configurations, bench, p), rootdir,
                             "gc_size_chart" + bench + "percentile_" + str(p) + "_sweep.png")
                for p in interesting_percentiles:
                    chart_md(md_file, size_compare_chart_gc_sweep(plt, parent_configurations, bench, p), rootdir,
                             "gc_size_chart" + bench + "percentile_" + str(p) + "_total.png")
                chart_md(md_file, size_compare_chart_gc_combined(plt, parent_configurations, bench), rootdir,
                         "gc_size_chart_total" + bench + ".png")

        if size_charts:
            for p in interesting_percentiles:
                chart_md(md_file, size_compare_chart(plt, parent_configurations, bench, p), rootdir,
                         "size_chart_" + bench + "percentile_" + str(p) + ".png")

        run = 3
        while run >= 0 and not any_run_exists(bench, configurations, run):
            run -= 1

        if run >= 0:
            chart_md(md_file, example_run_plot(plt, configurations, bench, run), rootdir,
                     "example_run_" + str(run) + "_" + bench + ".png")


def any_run_exists(bench, configurations, run):
    exits = False
    for conf in configurations:
        file = 'results/{}/{}/{}'.format(conf, bench, run)
        if os.path.exists(file):
            exits = True
            break
    return exits


def discover_benchmarks(configurations):
    benchmarks = []
    for conf in configurations:
        parent_folders = next(os.walk(os.path.join("results", conf)))[1]
        for pf in parent_folders:
            if is_subconfig(pf):
               for child in next(os.walk(os.path.join("results", conf, pf)))[1]:
                   if child not in benchmarks:
                       benchmarks.append(child)
            else:
                if pf not in benchmarks:
                    benchmarks.append(pf)

    return benchmarks


def is_subconfig(subconf):
    return subconf.startswith("size_") or subconf.startswith("gcthreads_")


if __name__ == '__main__':
    all_configs = next(os.walk("results"))[1]
    # added subconfigurations
    for conf in all_configs:
        folder = os.path.join("results", conf)
        subfolders = next(os.walk(folder))[1]
        for subconf in subfolders:
            if is_subconfig(subconf):
                all_configs.append(os.path.join(conf, subconf))

    results = generate_choices(all_configs)

    parser = argparse.ArgumentParser()
    parser.add_argument("--comment", help="comment at the suffix of the report name")
    parser.add_argument("--gc", help="enable charts about garbage collector", action="store_true")
    parser.add_argument("--vssize", help="enable charts against heap size", action="store_true")
    parser.add_argument("--benchmark", help="benchmarks to use in comparision", action='append')
    parser.add_argument("comparisons", nargs='*', choices=results + ["all"],
                        default="all")
    args = parser.parse_args()

    configurations = []
    if args.comparisons == "all":
        configurations = all_configs
    else:
        for arg in args.comparisons:
            configurations.append(expand_wild_cards(arg))

    comment = "_vs_".join(configurations).replace(os.sep, "_")
    if args.comment is not None:
        comment = args.comment

    parent_configurations = []
    for conf in configurations:
        if os.sep in conf:
            parent = os.path.split(conf)[0]
        else:
            parent = conf
        if parent not in parent_configurations:
            parent_configurations.append(parent)

    all_benchmarks = discover_benchmarks(parent_configurations)

    if args.benchmark != None:
        benchmarks = []
        for b in args.benchmark:
            benchmarks += filter(lambda s: s.startswith(b), all_benchmarks)
    else:
        benchmarks = all_benchmarks

    report_dir = "reports/summary_" + time.strftime('%Y%m%d_%H%M%S') + "_" + comment + "/"
    plt.rcParams["figure.figsize"] = [32.0, 24.0]
    plt.rcParams["font.size"] = 20.0
    mkdir(report_dir)
    with open(os.path.join(report_dir, "Readme.md"), 'w+') as md_file:
        write_md_file(report_dir, md_file, parent_configurations, configurations, benchmarks, args.gc, args.vssize)

    print report_dir
