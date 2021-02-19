import numpy as np
from shared.configurations import Configuration
from shared.parser import config_data
from shared.reports import Report
from shared.misc_utils import dict_write_arr, dict_get_arr

default_warmup = 500

class Comparison:
    def __init__(self, confs, warmup=default_warmup):
        assert len(confs) > 0

        configurations = []
        for item in confs:
            if isinstance(item, str):
                configurations.append(Configuration.from_results(item))
            else:
                configurations.append(item)
        self.configurations = configurations

        common_benchmarks = configurations[0].finished_benchmarks()
        for other_conf in configurations[1:]:
            present = set(other_conf.finished_benchmarks())
            common_benchmarks = list(filter(lambda b: b in present, common_benchmarks))
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
            except (IndexError, FileNotFoundError):
                res.append(0)
        return res

    def csv_file(self, data, path):
        with open(path, 'w+') as resultfile:
            leading = ['name']
            for conf in self.configurations:
                leading.append(conf.full_name)
            resultfile.write(','.join(leading) + '\n')
            for bench, res in zip(self.common_benchmarks, data):
                resultfile.write(','.join([str(bench)] + list(map(str, res))) + '\n')

    def simple_report(self, comment=None):
        report = Report(self, comment=comment)
        report.generate()
        return report

    @classmethod
    def from_dict(cls, kv):
        warmup = int(kv.get('warmup', default_warmup))
        confs = map(Configuration.from_dict, dict_get_arr(kv, 'confs'))
        return cls(confs, warmup)

    def to_dict(self):
        kv = {'warmup': self.warmup}
        conf_kvs = map(Configuration.to_dict, self.configurations)
        dict_write_arr(kv, 'confs', conf_kvs)

        return kv
