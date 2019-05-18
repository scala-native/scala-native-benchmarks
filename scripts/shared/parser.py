import numpy as np


def config_data(bench, conf, warmup):
    out = []
    for result_file in conf.benchmark_result_files(bench):
        try:
            raw_points = []
            with open(result_file) as data:
                for line in data.readlines():
                    try:
                        # in ms
                        raw_points.append(float(line) / 1000000)
                    except Exception as e:
                        print e
            out += raw_points[warmup:]
        except IOError:
            pass
    return np.array(out)