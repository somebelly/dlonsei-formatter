#!/usr/bin/env python3

import os, shlex, subprocess, argparse, sys, random
from natsort import natsorted
from lib import data, get_path_of, exist_in_library

if len(sys.argv) > 1:
    sys.argv.insert(1, '-k')


def parse_cli():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-k",
            "--keywords",
            nargs='+',
        )
        parser.add_argument(
            "-n",
            '--number',
            type=int,
            choices=range(1, 5),
        )
        parser.set_defaults(number=2)
        return parser.parse_args()
    except argparse.ArgumentError as err:
        print(str(err))
        sys.exit(2)


def find_audio_files(dir=os.getcwd(), exts=['.mp3', '.flac', '.mp4', '.webm']):
    return natsorted([
        "'" + os.path.join(root, file) + "'" for ext in exts
        for root, dirs, files in os.walk(dir) for file in files
        if file.lower().endswith(ext)
    ])


def find_cover(dir=os.getcwd(), exts=['.jpg', '.webp']):
    l = [
        os.path.join(root, file) for ext in exts
        for root, dirs, files in os.walk(dir) for file in files
        if file.lower().endswith(ext)
    ]
    if not l:
        return 'no'
    return "'" + sorted([(os.path.getsize(file), file) for file in l],
                        key=lambda s: s[0])[-1][1] + "'"


def get_rjcode_with(keywords):
    rjcodes = [key for key in data.keys() if isinstance(data[key], dict)]
    for keyword in keywords:
        rjcodes = [
            rjcode for rjcode in rjcodes for value in data[rjcode].values()
            if (keyword in value) or (keyword in rjcode)
        ]
    return rjcodes


args = parse_cli()

if not args.keywords:
    rjcodes_to_play = [
        random.choice(list(data.keys())) for _ in range(args.number)
    ]
else:
    rjcodes_to_play = [
        random.choice(get_rjcode_with(args.keywords))
        for _ in range(args.number)
    ]

rjcodes_to_play = [
    rjcode for rjcode in list(dict.fromkeys(rjcodes_to_play))
    if exist_in_library(rjcode)
]

print(rjcodes_to_play)

for rjcode in rjcodes_to_play:
    path = get_path_of(rjcode)
    playlist = ' '.join(find_audio_files(path))
    mpv = f'mpv --loop-playlist=no --external-file={find_cover(path)} --force-window --image-display-duration=inf --vid=1 {playlist}'
    subprocess.call(shlex.split(mpv))
