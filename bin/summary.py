from bench import benchmarks, runs, configurations

import numpy as np

def config_data(bench, conf):
    out = []
    for run in xrange(runs):
        with open('results/{}/{}/{}.data'.format(bench, conf['name'], run)) as data:
            for line in data.readlines():
                out.append(float(line))
    return np.array(out)

def peak_performance():
    out = []
    for bench in benchmarks:
        res = []
        for conf in configurations:
            res.append(np.percentile(config_data(bench, conf), 50))
        arr = np.array(res)
        normarr = arr / arr[0]
        out.append(normarr)
    return out

if __name__ == '__main__':
    leading = ['name']
    for conf in configurations:
        leading.append(conf['name'])
    print ','.join(leading)
    for bench, res in zip(benchmarks, peak_performance()):
        print ','.join([bench] + list(map(str, res)))
