from shared.configurations import default_runs, all_configs
from shared.benchmarks import all_benchmarks

import numpy as np

def config_data(bench, conf):
    out = []
    for run in xrange(default_runs):
        try:
            points = []
            with open('results/{}/{}/{}'.format(conf, bench, run)) as data:
                for line in data.readlines():
                    points.append(float(line))
            # take only last 2000 to account for startup
            points = points[-2000:]
            # filter out 1% worst measurements as outliers
            pmax = np.percentile(points, 99)
            for point in points:
                if point <= pmax:
                    out.append(point)
        except IOError:
            pass
    return np.array(out)

def peak_performance():
    out = []
    for bench in all_benchmarks:
        res = []
        for conf in all_configs:
            try:
                res.append(np.percentile(config_data(bench, conf), 10))
            except IndexError:
                res.append(0)
        out.append(res)
    return out

if __name__ == '__main__':
    leading = ['name']
    for conf in all_configs:
        leading.append(conf)
    print(','.join(leading))
    for bench, res in zip(all_benchmarks, peak_performance()):
        print(','.join([bench] + list(map(str, res))))

