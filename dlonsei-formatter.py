#!/usr/bin/env python3

from lib import format
import argparse, sys


def parse_cli():
    try:
        parser = argparse.ArgumentParser()
        # parser.add_argument(
        #     '-i',
        #     "--input",
        #     nargs='+',
        # )
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
        # parser.add_argument(
        #     "-cl",
        #     '--compression_level',
        #     dest='level',
        #     type=int,
        #     choices=range(13),
        # )
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
        parser.set_defaults(tag_files=True)
        parser.set_defaults(lossy=False)
        parser.set_defaults(convert=True)
        parser.set_defaults(save_cover=True)
        parser.set_defaults(metadata=False)
        # parser.set_defaults(level=5)
        return parser.parse_args()
    except argparse.ArgumentError as err:
        print(str(err))
        sys.exit(2)


args = parse_cli()

# if args.input:
#     for dir in args.input:
#         format(dir,
#                force=args.force,
#                convert=args.convert,
#                save_cover=args.save_cover)
# else:
#     format(force=args.force, convert=args.convert, save_cover=args.save_cover)

# format(force=args.force,
#        tag_files=args.tag_files,
#        lossy=args.lossy,
#        convert=args.convert,
#        save_cover=args.save_cover)

format(**vars(args))
