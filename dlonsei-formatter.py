#!/usr/bin/env python3

from lib import init, format
import argparse, sys


def parse_cli():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-i',
            "--input",
            nargs='+',
        )
        parser.add_argument(
            "-cl",
            '--compression_level',
            dest='level',
            type=int,
            choices=range(13),
        )
        parser.add_argument(
            '-r',
            '--replace',
            dest='replace',
            action='store_true',
        )
        parser.add_argument(
            '-nr',
            '--not-replace',
            dest='replace',
            action='store_false',
        )
        parser.set_defaults(inplace=True)
        parser.set_defaults(replace=False)
        parser.set_defaults(level=5)
        return parser.parse_args()
    except argparse.ArgumentError as err:
        print(str(err))
        sys.exit(2)


args = parse_cli()

init()
if args.input:
    for dir in args.input:
        format(dir)
else:
    format()
