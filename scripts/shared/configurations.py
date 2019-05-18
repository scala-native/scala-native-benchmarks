import os
import shutil as sh

from benchmarks import Benchmark
from file_utils import slurp, mkdir

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

        self.results_dir = os.path.join(results_path, self.name + suffix)
        print self.conf_dir

    @classmethod
    def from_results(cls, full_name):
        return cls.from_results_dir(os.path.join(results_path, full_name))

    @classmethod
    def from_results_dir(cls, full_path):
        name = None
        batches = None
        runs = None
        with open(os.path.join(full_path, 'settings.properties')) as settings:
            for line in settings.readlines():
                key, value = line.split('=')
                if key == 'name':
                    name = value
                elif key == 'batches':
                    batches = value
                elif key == 'runs':
                    runs = value
        if batches is None:
            batches = default_batches
        if runs is None:
            runs = default_runs
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
            .replace('$BENCH', bench) \
            .replace('$HOME', os.environ['HOME']) \
            .split(' ')

    def compile_cmd(self):
        return slurp(os.path.join(self.conf_dir, 'compile'))

    def write_settings(self):
        results_dir = self.results_dir
        with open(os.path.join(results_dir, 'settings.properties'), 'w+') as settings:
            settings.write('name={}\n'.format(self.name))
            settings.write('batches={}\n'.format(self.batches))
            settings.write('runs={}\n'.format(self.runs))

    def ensure_results_dir(self):
        dir = self.results_dir
        mkdir(dir)
        return dir

    def __str__(self):
        return self.name


all_configs = next(os.walk(confs_path))[1]

if 'GRAALVM_HOME' in os.environ:
    all_configs += [
        'native-image',
        'native-image-pgo',
    ]
