from shared.benchmarks import benchmarks
# from shared.configurations import configs
configs = [
    # "scala-native-0.4.0-2.11",
]

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
        for conf in configs:
            try:
                res.append(round(config_data(bench, conf) / 1e9, 2))
            except IndexError:
                res.append(0)
        out.append(res)
    return out

if __name__ == '__main__':
    leading = ['name']
    for conf in configs:
        leading.append(conf)
    print(','.join(leading))
    for (bench, batches), res in zip(benchmarks, compile_time()):
        print(','.join([bench] + list(map(str, res))))

