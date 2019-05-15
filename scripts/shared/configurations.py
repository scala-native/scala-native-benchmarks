import os
import shutil as sh

from shared.file_utils import slurp, mkdir

confs_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) + "/confs"

default_batches = 4000
default_runs = 20


class Configuration:

    def __init__(self, name, batches=default_batches, runs=default_runs):
        self.name = name
        self.conf_dir = os.path.join(confs_path, self.name)
        self.results_dir = os.path.join('results', self.name)
        self.batches = batches
        self.batch_size = 1
        self.runs = runs
        print self.conf_dir

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

    def run_cmd(self, bench):
        return slurp(os.path.join(self.conf_dir, 'run')) \
            .replace('$BENCH', bench) \
            .replace('$HOME', os.environ['HOME']) \
            .split(' ')

    def compile_cmd(self):
        return slurp(os.path.join(self.conf_dir, 'compile'))

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
