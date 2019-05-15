import os

from shared.file_utils import sbt, run, slurp, mkdir


class Benchmark:

    def __init__(self, name):
        self.name = name

    def compile(self, conf):
        cmd = [sbt, '-J-Xmx6G', 'clean']
        cmd.append('set mainClass in Compile := Some("{}")'.format(self.name))
        cmd.append(conf.compile_cmd())
        return run(cmd)

    def run(self, conf):
        run_cmd = conf.run_cmd()
        input = slurp(os.path.join('input', self.name))
        output = slurp(os.path.join('output', self.name))
        cmd = []
        cmd.extend(run_cmd)
        cmd.extend([str(conf.batches), str(conf.batch_size), input, output])

    def ensure_results_dir(self, conf):
        dir = os.path.join(conf.ensure_results_dir(), self.name)
        mkdir(dir)
        return dir

    def __str__(self):
        return self.name
