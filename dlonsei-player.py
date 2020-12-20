#!/usr/bin/env python3

import os, shlex, subprocess, argparse, sys, random
import pprint
from pathlib import Path
from natsort import natsorted
from lib import data

if len(sys.argv) > 1:
    sys.argv.insert(1, '-k')

pp = pprint.PrettyPrinter(indent=4)


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
        # parser.add_argument(
        #     "-v",
        #     '--show_video',
        #     dest='video',
        #     action='store_true',
        # )
        parser.set_defaults(number=2)
        # parser.set_defaults(video=False)
        return parser.parse_args()
    except argparse.ArgumentError as err:
        print(str(err))
        sys.exit(2)


def find_audio_files(
        _dir=os.getcwd(), exts=['.mp3', '.flac', '.mp4', '.m4a', '.webm']):
    return natsorted([
        '"' + os.path.join(root, file) + '"' for ext in exts
        for root, dirs, files in os.walk(_dir) for file in files
        if file.lower().endswith(ext)
    ])


def find_cover(_dir=os.getcwd(), exts=['.jpg', '.webp']):
    l = [
        os.path.join(root, file) for ext in exts
        for root, dirs, files in os.walk(_dir) for file in files
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


def print_rjcode(_rjcode):
    print()
    print('========')
    print(_rjcode)
    print('========')
    _path = data[_rjcode]['Path']
    for k in data[_rjcode].keys():
        if k not in ['img', 'Path', 'ファイル容量', 'ファイル形式']:
            print(f'  {k}:  \t{data[_rjcode][k]}')
    print(Path(_path).as_uri())
    cover = find_cover(_path)
    if cover[1:-1]:
        print(Path(cover[1:-1]).as_uri())
    print()


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

rjcodes_to_play = [rjcode for rjcode in list(dict.fromkeys(rjcodes_to_play))]

for rjcode in rjcodes_to_play:
    print_rjcode(rjcode)
    path = data[rjcode]['Path']
    playlist = ' '.join(find_audio_files(path))
    # if args.video:
    #     mpv = f'mpv --loop-playlist=no --external-file={cover} --force-window --image-display-duration=inf --vid=1 {playlist}'
    # else:
    mpv = f'mpv --loop-playlist=no --no-video {playlist}'
    subprocess.call(shlex.split(mpv))
