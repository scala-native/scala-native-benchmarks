from run import benchmarks, runs, configurations

import numpy as np

def config_data(bench, conf):
    try:
        with open('results/{}/{}/compile_time'.format(conf, bench)) as data:
            return float(data.read())
    except IOError:
        return 0

def compile_time():
    out = []
    for bench in benchmarks:
        res = []
        for conf in configurations:
            try:
                res.append(np.percentile(config_data(bench, conf), 10))
            except IndexError:
                res.append(0)
        out.append(res)
    return out

if __name__ == '__main__':
    leading = ['name']
    for conf in configurations:
        leading.append(conf)
    print(','.join(leading))
    for bench, res in zip(benchmarks, compile_time()):
        print(','.join([bench] + list(map(str, res))))

