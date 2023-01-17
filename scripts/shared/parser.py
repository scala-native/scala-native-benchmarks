import numpy as np


def config_data(bench, conf, warmup):
    out = []
    avgNoWarmup = []
    avgWithWarmup = []
    for result_file in conf.benchmark_result_files(bench):
        try:
            raw_points = []
            with open(result_file) as data:
                for line in data.readlines():
                    try:
                        # in ms
                        raw_points.append(float(line) / 1000000)
                    except Exception as e:
                        print(e)
            avgNoWarmup.append(np.average(raw_points))
            avgWithWarmup.append(np.average(raw_points[warmup:]))
            out += raw_points[warmup:]
        except IOError:
            pass

    stdDevWithWarmup = np.std(avgWithWarmup) / np.average(avgWithWarmup)
    stdDevNoWarmup = np.std(avgNoWarmup) / np.average(avgNoWarmup)
    print(bench.name, ",", conf.name, ",", stdDevWithWarmup, ",", stdDevNoWarmup, ",", len(avgWithWarmup))

    return np.array(out)