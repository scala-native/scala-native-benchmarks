#!/usr/bin/env python
import argparse

from shared.cmdline import expand_all
from shared.benchmarks import benchmarks
from shared.configurations import Configuration, default_runs, default_batches

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", help="number of runs", type=int, default=default_runs)
    parser.add_argument("--batches", help="number of batches per run", type=int, default=default_batches)
    parser.add_argument("configurations", nargs='*', default=[None])
    args = parser.parse_args()

    configuration_names = expand_all(args.configurations)
    print("configurations:", configuration_names)

    for conf_name in configuration_names:
        Configuration(conf_name, batches=args.batches, runs=args.runs).run_benchmarks(benchmarks)
