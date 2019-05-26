import os
import shutil as sh

from benchmarks import Benchmark
from file_utils import slurp, mkdir, dict_from_file, dict_to_file

confs_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) + "/confs"
results_path = 'results'

default_batches = 4000
default_runs = 20


class Configuration:

    def __init__(self, name, batches=default_batches, runs=default_runs):
        self.name = name
        self.conf_dir = os.path.join(confs_path, self.name)
        self.batches = batches
        self.batch_size = 1
        self.runs = runs

        suffix = ""
        if runs != default_runs:
            suffix += "-r" + str(runs)
        if batches != default_batches:
            suffix += "-b" + str(batches)

        self.full_name = self.name + suffix
        self.results_dir = os.path.join(results_path, self.full_name)
        self.settings_file = os.path.join(self.results_dir, 'settings.properties')

    @classmethod
    def from_results(cls, full_name):
        return cls.from_results_dir(os.path.join(results_path, full_name))

    @classmethod
    def from_results_dir(cls, full_path):
        settings_file = os.path.join(full_path, 'settings.properties')
        kv = dict_from_file(settings_file)
        return cls.from_dict(kv)

    @classmethod
    def from_dict(cls, kv):
        batches = int(kv.get('batches', default_batches))
        runs = int(kv.get('runs', default_runs))
        name = kv.get('name')
        return cls(name, batches=batches, runs=runs)

    def make_active(self):
        build_sbt_src = os.path.join(self.conf_dir, 'build.sbt')
        if os.path.exists(build_sbt_src):
            sh.copyfile(build_sbt_src, 'build.sbt')
        else:
            os.remove('build.sbt')

        plugins_sbt_src = os.path.join(self.conf_dir, 'plugins.sbt')
        if os.path.exists(plugins_sbt_src):
            sh.copyfile(plugins_sbt_src, 'project/plugins.sbt')
        else:
            os.remove('project/plugins.sbt')

    def run_benchmarks(self, benchmarks):
        self.make_active()
        for item in benchmarks:
            if isinstance(item, basestring):
                bench = Benchmark(item)
            else:
                bench = item
            print('--- conf: {}, bench: {}'.format(self.name, bench))

            bench.compile(self)
            results_dir = bench.ensure_results_dir(self)

            runs = self.runs
            for n in xrange(runs):
                print('--- run {}/{}'.format(n, runs))

                out = bench.run(self)
                with open(os.path.join(results_dir, str(n)), 'w+') as resultfile:
                    resultfile.write(out)

    def run_cmd(self, bench):
        return slurp(os.path.join(self.conf_dir, 'run')) \
            .replace('$BENCH', bench.name) \
            .replace('$HOME', os.environ['HOME']) \
            .split(' ')

    def compile_cmd(self):
        return slurp(os.path.join(self.conf_dir, 'compile'))

    def to_dict(self):
        return {'name': self.name, 'batches': self.batches, 'runs': self.runs}

    def write_settings(self):
        settings_file = self.settings_file
        kv = self.to_dict()
        dict_to_file(settings_file, kv)

    def ensure_results_dir(self):
        results_dir = self.results_dir
        mkdir(results_dir)
        self.write_settings()
        return results_dir

    def finished_benchmarks(self):
        benchmarks = []
        results_dir = self.results_dir
        all_subdirs = next(os.walk(results_dir))[1]
        for subdir in all_subdirs:
            all_runs_present = True
            for run in xrange(self.runs):
                if not os.path.isfile(os.path.join(results_dir, subdir, str(run))):
                    all_runs_present = False
                    break
            if all_runs_present:
                benchmarks.append(Benchmark(subdir))

        return benchmarks

    def benchmark_result_files(self, benchmark):
        benchmark_dir = benchmark.results_dir(self)
        for run in xrange(self.runs):
            yield os.path.join(benchmark_dir, str(run))

    def __str__(self):
        s = '{}('.format(self.name)
        s += 'runs={}'.format(str(self.runs))
        if self.runs == default_runs:
            s += '[default]'
        s += ', batches={}'.format(str(self.batches))
        if self.batches == default_batches:
            s += '[default]'
        s += ') = {}'.format(self.full_name)
        return s


all_configs = next(os.walk(confs_path))[1]

if 'GRAALVM_HOME' in os.environ:
    all_configs += [
        'native-image',
        'native-image-pgo',
    ]
