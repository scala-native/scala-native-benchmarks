#!/usr/bin/env python
import argparse

from shared.cmdline import expand_all
from shared.comparison import Comparison, default_warmup

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--warmup", help="number of iterations to skip before calculating percentiles", type=int, default=default_warmup)
    parser.add_argument("configurations", nargs='*', default=[None])
    args = parser.parse_args()

    configuration_names = expand_all(args.configurations)
    comparison = Comparison(configuration_names, warmup=args.warmup)
    comparison.simple_report()
