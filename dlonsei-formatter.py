#!/usr/bin/env python3

import sys
import argparse
from lib import formatter


def parse_cli():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-f",
            '--force',
            dest='force',
            action='store_true',
        )
        parser.add_argument(
            '-nr',
            '--not_remove_metadata',
            dest='metadata',
            action='store_true',
        )
        parser.add_argument(
            '-nt',
            '--not_tag_files',
            dest='tag_files',
            action='store_false',
        )
        parser.add_argument(
            '--lossy',
            dest='lossy',
            action='store_true',
        )
        parser.add_argument(
            '-nc',
            '--not_convert',
            dest='convert',
            action='store_false',
        )
        parser.add_argument(
            '-nsc',
            '--not_save_cover',
            dest='save_cover',
            action='store_false',
        )

        parser.set_defaults(force=False)
        parser.set_defaults(tag_files=False)
        parser.set_defaults(lossy=False)
        parser.set_defaults(convert=True)
        parser.set_defaults(save_cover=False)
        parser.set_defaults(metadata=False)
        return parser.parse_args()
    except argparse.ArgumentError as err:
        print(str(err))
        sys.exit(2)


args = parse_cli()
formatter(**vars(args))
