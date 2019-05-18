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
        print common_benchmarks
        for other_conf in configurations[1:]:
            present = set(other_conf.finished_benchmarks())
            common_benchmarks = filter(lambda b: b in present, common_benchmarks)
            print common_benchmarks
        self.common_benchmarks = common_benchmarks
        self.warmup = warmup

    def peak_performances(self):
        out = []
        for bench in self.common_benchmarks:
            res = []
            for conf in self.configurations:
                try:
                    res.append(np.percentile(config_data(bench, conf, self.warmup), 50))
                except IndexError:
                    res.append(0)
            out.append(res)
        return out

    def simple_report(self):
        leading = ['name']
        for conf in self.configurations:
            leading.append(conf.full_name)
        print ','.join(leading)
        for bench, res in zip(self.common_benchmarks, self.peak_performances()):
            print ','.join([str(bench)] + list(map(str, res)))