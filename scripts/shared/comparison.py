import numpy as np
from configurations import Configuration
from parser import config_data

default_warmup = 2000


class Comparison:
    def __init__(self, confs, warmup=default_warmup):
        assert len(confs) > 0

        configurations = []
        for item in confs:
            if isinstance(item, basestring):
                configurations.append(Configuration.from_results(item))
            else:
                configurations.append(item)
        self.configurations = configurations

        common_benchmarks = configurations[0].finished_benchmarks()
        for other_conf in configurations[1:]:
            present = set(other_conf.finished_benchmarks())
            common_benchmarks = filter(lambda b: b in present, common_benchmarks)
        self.common_benchmarks = common_benchmarks
        self.warmup = warmup

    def percentile(self, p):
        out = []
        for bench in self.common_benchmarks:
            out.append(self.percentile_bench(bench, p))
        return out

    def percentile_bench(self, bench, p):
        res = []
        for conf in self.configurations:
            try:
                res.append(np.percentile(config_data(bench, conf, self.warmup), p))
            except IndexError:
                res.append(0)
        return res

    def simple_report(self):
        leading = ['name']
        for conf in self.configurations:
            leading.append(conf.full_name)
        print ','.join(leading)
        for bench, res in zip(self.common_benchmarks, self.percentile(50)):
            print ','.join([str(bench)] + list(map(str, res)))