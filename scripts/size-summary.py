from shared.benchmarks import benchmarks
from shared.configurations import configs, default_runs
import os
import numpy as np

def config_data(bench, conf):
    try:
        return len(open('binaries/{}/{}'.format(conf, bench), 'rb').read())
    except IOError:
        return 0

def binary_size():
    out = []
    for bench in benchmarks:
        res = []
        for conf in configs:
            try:
                res.append(np.percentile(config_data(bench, conf), 10))
            except IndexError:
                res.append(0)
        out.append(res)
    return out

if __name__ == '__main__':
    leading = ['name']
    for conf in configs:
        leading.append(conf)
    print(','.join(leading))
    for bench, res in zip(benchmarks, binary_size()):
        print(','.join([bench] + list(map(str, res))))

