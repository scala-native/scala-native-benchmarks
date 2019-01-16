#!/usr/bin/env python2
import os
import errno
import subprocess as subp
import shutil as sh
import argparse
import multiprocessing as mp
import itertools



def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def slurp(path):
    with open(path) as f:
        return f.read().strip()


def where(cmd):
    if os.path.isfile(cmd):
        return cmd
    else:
        paths = os.environ['PATH'].split(os.pathsep)
        for p in paths:
            f = os.path.join(p, cmd)
            if os.path.isfile(f):
                return f
        else:
            return None


def try_run(cmd, env=None, wd=None):
    try:
        print run(cmd, env, wd)
        return True
    except subp.CalledProcessError as err:
        print err.output
        return False


def try_run_silent(cmd, env=None, wd=None):
    try:
        run(cmd, env, wd)
        return True
    except subp.CalledProcessError as err:
        print err.output
        return False


def run(cmd, env=None, wd=None):
    print(">>> " + str(cmd))
    if wd == None:
        return subp.check_output(cmd, stderr=subp.STDOUT, env=env)
    else:
        return subp.check_output(cmd, stderr=subp.STDOUT, env=env, cwd=wd)


scala_native_dir = os.path.join("..", "scala-native")
upload_dir = os.path.abspath(os.path.join("..", "scala-native-benchmark-results"))
local_scala_repo_dir = os.path.abspath(os.path.join("..", "scala-2.11.11-only"))


def git_add(dir, *items):
    return try_run(["git", "add"] + list(items), wd=dir)


def git_commit(dir, msg):
    return try_run(["git", "commit", "-m", msg], wd=dir)


def git_pull(dir):
    my_env = os.environ.copy()
    my_env["GIT_MERGE_AUTOEDIT"] = "no"
    return try_run(["git", "pull"], env=my_env, wd=dir)


def git_push(dir):
    return try_run(['git', 'push'], wd=dir)


def git_fetch(dir):
    return try_run(['git', 'fetch', '--all'], wd=dir)


def get_ref(ref):
    git_rev_parse = ['git', 'rev-parse', '--short', ref]
    try:
        return run(git_rev_parse, wd=scala_native_dir).strip()
    except subp.CalledProcessError as err:
        out = err.output
        print "Cannot find", ref, "!"
        print out
        return None


def compile_scala_native(ref, sha1):
    if ref != "HEAD":
        git_checkout = ['git', 'checkout', sha1]
        try:
            print run(git_checkout, wd=scala_native_dir)
        except subp.CalledProcessError as err:
            out = err.output
            print "Cannot checkout", sha1, "!"
            print out
            return False

    compile_cmd = [sbt, '-no-colors', '-J-Xmx2G', 'rebuild', 'sandbox/run']
    compile_env = os.environ.copy()
    compile_env["SCALANATIVE_GC"] = "immix"
    if os.path.isdir(local_scala_repo_dir):
        compile_env["SCALANATIVE_SCALAREPO"] = local_scala_repo_dir

    try:
        run(compile_cmd, compile_env, wd=scala_native_dir)
        return True
    except subp.CalledProcessError as err:
        out = err.output
        print "Compilation failure!"
        print out
        return False


def compile(conf, bench, compilecmd, debug, trace, extra_args):
    cmd = [sbt, '-no-colors', '-J-Xmx2G', 'clean']
    cmd.append('set mainClass in Compile := Some("{}")'.format(bench))
    if conf.startswith("scala-native"):
        if debug or trace:
            cmd.append('set nativeCompileOptions ++= Seq("-g", "-DDEBUG_ASSERT")')
        if trace:
            cmd.append('set nativeCompileOptions +="-DDEBUG_PRINT"')
        for k,v in extra_args.iteritems():
            if k.endswith("?"):
                cmd.append('set nativeCompileOptions +="-D{}"'.format(k[:-1]))
            else:
                cmd.append('set nativeCompileOptions +="-D{}={}"'.format(k,v))
    cmd.append(compilecmd)
    return try_run_silent(cmd)


sbt = where('sbt')

default_benchmarks = [
    'bounce.BounceBenchmark',
    'list.ListBenchmark',
    'richards.RichardsBenchmark',
    'queens.QueensBenchmark',
    'permute.PermuteBenchmark',
    'deltablue.DeltaBlueBenchmark',
    'tracer.TracerBenchmark',
    'brainfuck.BrainfuckBenchmark',
    'json.JsonBenchmark',
    'cd.CDBenchmark',
    'kmeans.KmeansBenchmark',
    'gcbench.GCBenchBenchmark',
    'mandelbrot.MandelbrotBenchmark',
    'nbody.NbodyBenchmark',
    'sudoku.SudokuBenchmark',
]

all_benchmarks = default_benchmarks + [
    'histogram.Histogram',
]

stable = 'scala-native-0.3.8'
latest = 'scala-native-0.3.9-SNAPSHOT'
baseline = [
    'jvm',
    stable,
]
default = baseline + [latest]

confs_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + "/confs"

configurations = all_configs = next(os.walk(confs_path))[1]

graalvm = [
    'native-image',
    'native-image-pgo',
]

if 'GRAALVM_HOME' in os.environ:
    baseline += graalvm
else:
    for g in graalvm:
        all_configs.remove(g)

default_runs = 20
default_batches = 3000
default_par = 1
batch_size = 1


def expand_wild_cards(arg):
    if arg.startswith("latest"):
        return latest + arg[len("latest"):]
    elif arg.startswith("stable"):
        return stable + arg[len("stable"):]
    else:
        return arg


def benchmark_parse(arg):
    parts = arg.split("@")
    if len(parts) == 2:
        return parts[0], parts[1]
    else:
        return arg, None


def ref_parse(arg):
    parts = arg.split("@")
    if len(parts) == 3:
        return parts[0], (parts[2] + "/" + parts[1])
    elif len(parts) == 2:
        return parts[0], parts[1]
    else:
        return arg, None


def size_parse(arg):
    parts = arg.split(":")
    if len(parts) == 1:
        return [arg, arg]
    else:
        return parts


def generate_choices(direct_choices):
    results = direct_choices
    for dir in direct_choices:
        if dir.startswith(latest):
            results += ["latest" + dir[len(latest):]]
        if dir.startswith(stable):
            results += ["stable" + dir[len(stable):]]
    return results


def single_run(to_run):
    n = to_run["n"]
    runs = to_run["runs"]
    unexpanded_cmd = to_run["cmd"]
    resultsdir = to_run["resultsdir"]
    conf = to_run["conf"]
    bench = to_run["bench"]
    gcstats = to_run["gcstats"]
    minsize = to_run["size"][0]
    maxsize = to_run["size"][1]
    gcThreads = to_run["gcThreads"]

    print('--- run {}/{}'.format(n, runs))
    my_env = os.environ.copy()
    if gcstats:
        my_env["SCALANATIVE_STATS_FILE"] = os.path.join(resultsdir, str(n) + ".gc.csv")

    if minsize != "default":
        my_env["SCALANATIVE_MIN_HEAP_SIZE"] = minsize
    elif "SCALANATIVE_MIN_HEAP_SIZE" in my_env:
        del my_env["SCALANATIVE_MIN_HEAP_SIZE"]

    if maxsize != "default":
        my_env["SCALANATIVE_MAX_HEAP_SIZE"] = maxsize
    elif "SCALANATIVE_MAX_HEAP_SIZE" in my_env:
        del my_env["SCALANATIVE_MAX_HEAP_SIZE"]

    if gcThreads != "default":
        my_env["SCALANATIVE_GC_THREADS"] = gcThreads
    elif "SCALANATIVE_GC_THREADS" in my_env:
        del my_env["SCALANATIVE_GC_THREADS"]

    cmd = []
    for token in unexpanded_cmd:
        if token == "$JAVA_ARGS":
            if minsize != "default":
                cmd += ["-Xms" + minsize]
            if maxsize != "default":
                cmd += ["-Xmx" + maxsize]
            if gcstats:
                cmd += ["-XX:+PrintGCApplicationStoppedTime", "-Xloggc:" + os.path.join(resultsdir, str(n) + ".gc.txt")]
        else:
            cmd += [token]

    try:
        out = run(cmd, my_env)
        with open(os.path.join(resultsdir, str(n)), 'w+') as resultfile:
            resultfile.write(out)
        return []
    except subp.CalledProcessError as err:
        out = err.output
        print "Failure!"
        print out
        with open(os.path.join(resultsdir, str(n) + ".failed"), 'w+') as failfile:
            failfile.write(out)
        return [dict(conf=conf, bench=bench, run=n)]


def upload(subconfig_dir, symlink, use_git, overwrite):
    if os.path.isdir(upload_dir):
        target = os.path.join(upload_dir, subconfig_dir)
        targetComplete = os.path.isfile(os.path.join(target, ".complete"))
        targetExisted = os.path.isdir(target)
        if (targetComplete and overwrite) or targetExisted:
            mkdir(os.path.join("..", target))
            sh.rmtree(target, ignore_errors=True)
        if not targetExisted or overwrite:
            sh.copytree(subconfig_dir, target, symlinks=True)
            if use_git:
                if symlink != None:
                    git_add(upload_dir, symlink)
                if git_add(upload_dir, target) \
                        and git_commit(upload_dir, "automated commit " + subconfig_dir) \
                        and git_pull(upload_dir) \
                        and git_push(upload_dir):
                    pass
    else:
        print "WARN", upload_dir, "does not exist!"


def create_symlink(generalized_dir, root_dir):
    try:
        os.unlink(generalized_dir)
    except:
        pass
    print "creating symlink", generalized_dir, "->", root_dir
    os.symlink(os.path.split(root_dir)[1], generalized_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--suffix", help="suffix added to results")
    parser.add_argument("--runs", help="number of runs", type=int, default=default_runs)
    parser.add_argument("--batches", help="number of batches per run", type=int, default=default_batches)
    parser.add_argument("--benchmark", help="benchmarks to run", action='append')
    parser.add_argument("--argnames", help="compile arguments to set, mark flags with a '?' at the end, split with ','", type=str)
    parser.add_argument("--argv", help="argument values, split with ',', booleans as true or false", action='append')
    parser.add_argument("--size", help="different size settings to use", action='append')
    parser.add_argument("--gcthreads", help="different number of garbage collection threads to use", action='append')
    parser.add_argument("--par", help="number of parallel processes", type=int, default=default_par)
    parser.add_argument("--gc", help="gather gc statistics", action="store_true")
    parser.add_argument("--upload", help="copy the results to ../scala-native-benchmark-results", action="store_true")
    parser.add_argument("--gitupload", help="copy the results to ../scala-native-benchmark-results and commit and push to git", action="store_true")
    parser.add_argument("--overwrite", help="overwrite old results", action="store_true")
    parser.add_argument("--append", help="do not delete old data", action="store_true")
    parser.add_argument("--gcdebug", help="enable debug for GCs", action="store_true")
    parser.add_argument("--gctrace", help="verbose logging for GCs to stdout", action="store_true")
    parser.add_argument("set", nargs='*', default="default")
    args = parser.parse_args()
    print args

    runs = args.runs
    batches = args.batches
    par = args.par

    if args.benchmark != None:
        benchmarks = []
        for b in args.benchmark:
            if b == "default":
                benchmarks += default_benchmarks
            else:
                bname, bargs = benchmark_parse(b)
                matching = filter(lambda s: s.startswith(bname), all_benchmarks)
                if bargs != None:
                    benchmarks += map(lambda x: (x, bargs), matching)
                else:
                    benchmarks += matching
    else:
        benchmarks = default_benchmarks

    if args.size != None:
        sizes = []
        for subconf_str in args.size:
            parsed = size_parse(subconf_str)
            if parsed == ["default", "default"]:
                sizes = [parsed] + sizes
            else:
                sizes += [parsed]
    else:
        sizes = [["default", "default"]]

    if args.gcthreads != None:
        gcThreadCounts = args.gcthreads
    else:
        gcThreadCounts = ["default"]

    configurations = []
    for choice in args.set:
        expanded = expand_wild_cards(choice)
        if expanded == "baseline":
            configurations += baseline
        elif expanded == "default":
            configurations = default
        else:
            configurations += [expanded]

    print "configurations:", configurations
    print "benchmarks:", benchmarks
    print "heap sizes:", sizes
    print "GC thread counts:", gcThreadCounts

    should_fetch = False
    for conf in configurations:
        if '@' in conf and not conf.endswith("@HEAD"):
            should_fetch = True
            break

    if args.argnames != None and args.argv != None:
        derived_configs = []
        argnames = args.argnames.split(",")
        for valset in args.argv :
            values = valset.split(",")
            suffix = "-a" + ("-".join(values))
            extra_args = dict()
            for (name, value) in zip(argnames, values):
                if name.endswith("?"):
                    if value in ["1", "true", "TRUE", "True"]:
                        extra_args[name[:-1]] = True
                else:
                    extra_args[name] = value
            derived_configs.append((suffix, extra_args))
    else:
        derived_configs = [("", dict())]

    if should_fetch:
        git_fetch(scala_native_dir)

    suffix = ""
    if runs != default_runs:
        suffix += "-r" + str(runs)
    if batches != default_batches:
        suffix += "-b" + str(batches)
    if par != default_par:
        suffix += "-p" + str(par)
    if args.gc:
        suffix += "-gc"
    if args.gcdebug:
        suffix += "-gcdebug"
    if args.gctrace:
        suffix += "-gctrace"
    if args.suffix is not None:
        suffix += "_" + args.suffix

    failed = []
    skipped = []
    compile_fail = []
    result_dirs = []
    symlinks = []

    pool = None
    if par > 1:
        pool = mp.Pool(par)

    for conf in configurations:
        conf_name, ref = ref_parse(conf)

        if ref == None:
            sha1 = None
        else:
            sha1 = get_ref(ref)
            if sha1 == None:
                compile_fail += [conf]
                continue

        if sha1 != None:
            success = compile_scala_native(ref, sha1)
            if not success:
                compile_fail += [conf]
                continue

        # derived configurations
        for (der_suffix, extra_args) in derived_configs:
            generalized_dir = os.path.join('results', conf + suffix + der_suffix)
            if sha1 == None:
                root_dir = generalized_dir + der_suffix
            else:
                root_dir = os.path.join('results', conf + "." + sha1 + "." + suffix + der_suffix)

            mkdir(root_dir)
            symlink = None
            if generalized_dir != root_dir:
                create_symlink(generalized_dir, root_dir)
                symlinks += [[generalized_dir, root_dir]]
                symlink = generalized_dir
                if args.upload or args.gitupload:
                    create_symlink(os.path.join(upload_dir, generalized_dir), root_dir)

            # subconfigurations
            for (size, gcThreads) in itertools.product(sizes, gcThreadCounts):

                if size == ["default", "default"] and gcThreads == "default":
                    subconfig_dir = root_dir
                else:
                    size_str = []
                    if size != ["default", "default"] :
                        size_str = ["size_" + size[0] + "-" + size[1]]
                    gcThreads_str = []
                    if gcThreads != "default":
                        gcThreads_str = ["gcthreads_" + gcThreads]
                    subconf_str = "_".join(size_str + gcThreads_str)
                    subconfig_dir = os.path.join(root_dir, subconf_str)

                if not args.overwrite and os.path.isfile(os.path.join(subconfig_dir, ".complete")):
                    print  subconfig_dir, "already complete, skipping"
                    skipped += [subconfig_dir]
                    continue

                if not args.append:
                    sh.rmtree(subconfig_dir, ignore_errors=True)

                mkdir(subconfig_dir)

                for bconf in benchmarks:
                    if type(bconf) is tuple:
                        bench, input = bconf
                        bfullname = bench + "@" + input
                    else:
                        bench = bconf
                        input = slurp(os.path.join('input', bench))
                        bfullname = bench
                    print('--- heap size: {} GC threads: {} conf: {}, bench: {}'.format(size, gcThreads, conf, bfullname))

                    output = slurp(os.path.join('output', bench))
                    compilecmd = slurp(os.path.join('confs', conf_name, 'compile'))
                    runcmd = slurp(os.path.join('confs', conf_name, 'run')) \
                        .replace('$BENCH', bench) \
                        .replace('$HOME', os.environ['HOME']).split(' ')

                    if os.path.exists(os.path.join('confs', conf_name, 'build.sbt')):
                        sh.copyfile(os.path.join('confs', conf_name, 'build.sbt'), 'build.sbt')
                    else:
                        os.remove('build.sbt')

                    if os.path.exists(os.path.join('confs', conf_name, 'plugins.sbt')):
                        sh.copyfile(os.path.join('confs', conf_name, 'plugins.sbt'), 'project/plugins.sbt')
                    else:
                        os.remove('project/plugins.sbt')

                    compile_success = compile(conf, bench, compilecmd, args.gcdebug, args.gctrace, extra_args)
                    if not compile_success:
                        compile_fail += [conf]
                        break

                    resultsdir = os.path.join(subconfig_dir, bfullname)
                    print "results in", resultsdir
                    mkdir(resultsdir)

                    cmd = []
                    cmd.extend(runcmd)
                    cmd.extend([str(batches), str(batch_size), input, output])

                    to_run = []
                    for n in xrange(runs):
                        to_run += [
                            dict(runs=runs, cmd=cmd, resultsdir=resultsdir, conf=conf, bench=bench, n=n, gcstats=args.gc,
                                 size=size, gcThreads=gcThreads)]

                    if par == 1:
                        for tr in to_run:
                            failed += single_run(tr)
                    else:
                        failed += sum(pool.map(single_run, to_run), [])

                # mark it as complete
                open(os.path.join(subconfig_dir, ".complete"), 'w+').close()
                result_dirs += [subconfig_dir]

                if args.upload or args.gitupload:
                    upload(subconfig_dir, symlink, args.gitupload, args.overwrite)

    print "results:"
    for dir in result_dirs:
        print dir

    if len(symlinks) > 0:
        print("{} symlinks ".format(len(symlinks)))
        for symlink in symlinks:
            print symlink[0], "->", symlink[1]


    if len(compile_fail) > 0:
        print("{} compilation failed ".format(len(failed)))
        for skip in compile_fail:
            print skip

    if len(skipped) > 0:
        print("{} benchmarks skipped ".format(len(failed)))
        for skip in skipped:
            print skip

    if len(failed) > 0:
        print("{} benchmarks failed ".format(len(failed)))
        for fail in failed:
            print fail

    if len(compile_fail) > 0 or len(failed) > 0:
        exit(1)
