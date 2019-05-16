#!/usr/bin/env python
import argparse

from shared.benchmarks import all_benchmarks
from shared.configurations import Configuration, default_runs, default_batches

stable = 'scala-native-0.3.9'
latest = 'scala-native-0.4.0-SNAPSHOT'


def expand_wild_cards(arg):
    if arg is None:
        return arg
    elif arg.startswith("latest"):
        return latest + arg[len("latest"):]
    elif arg.startswith("stable"):
        return stable + arg[len("stable"):]
    else:
        return arg


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="interactive mode", action="store_true")
    parser.add_argument("--runs", help="number of runs", type=int, default=default_runs)
    parser.add_argument("--batches", help="number of batches per run", type=int, default=default_batches)
    parser.add_argument("set", nargs='*', default=[None])
    args = parser.parse_args()
    print args

    if args.i:
        from IPython import embed
        embed()
    else:
        configurations = []
        for choice in args.set:
            expanded = expand_wild_cards(choice)
            if expanded is None:
                configurations = [stable, latest]
            else:
                configurations += [expanded]

        print "configurations:", configurations

        for conf_name in configurations:
            Configuration(conf_name, batches=args.batches, runs=args.runs).run_benchmarks(all_benchmarks)
