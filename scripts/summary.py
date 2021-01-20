from run import benchmarks, runs, configurations

import numpy as np

def config_data(bench, conf):
    out = []
    for run in range(runs):
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
    for bench in benchmarks:
        res = []
        for conf in configurations:
            try:
                res.append(np.percentile(config_data(bench, conf), 50))
            except IndexError:
                res.append(0)
        out.append(res)
    return out

if __name__ == '__main__':
    leading = ['name']
    for conf in configurations:
        leading.append(conf)
    print(','.join(leading))
    for bench, res in zip(benchmarks, peak_performance()):
        print(','.join([bench] + list(map(str, res))))
