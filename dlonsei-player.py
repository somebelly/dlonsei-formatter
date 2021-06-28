#!/usr/bin/env python3

import os
import shlex
import subprocess
import argparse
import sys
import random
import pprint
import json
from pathlib import Path
from natsort import natsorted
from lib import local_data

with open(local_data, 'r+') as _f:
    data = json.load(_f)
    assert 'library_dir' in data

    to_del = [
        _k for _k in data if 'Path' in data[_k] and
        not os.path.exists(os.path.join(data['library_dir'], data[_k]['Path']))
    ]
    for _k in to_del:
        del data[_k]
    _f.seek(0)
    json.dump(data, _f, indent=4, ensure_ascii=False)
    _f.truncate()

if len(sys.argv) > 1 and '-n' not in sys.argv and '--number' not in sys.argv:
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
            choices=range(1, 13),
        )
        parser.set_defaults(number=5)
        return parser.parse_args()
    except argparse.ArgumentError as err:
        print(str(err))
        sys.exit(2)


def find_audio_files(_dir=os.getcwd(), exts=None):
    if exts is None:
        exts = ['.mp3', '.mp4', '.webm', '.flac']
    return natsorted([
        '"' + os.path.join(root, file) + '"' for ext in exts
        for root, dirs, files in os.walk(_dir) for file in files
        if file.lower().endswith(ext)
    ])


def find_cover(_dir=os.getcwd(), exts=None):
    if exts is None:
        exts = ['.jpg', '.webp', '.png']
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

for rjcode in rjcodes_to_play:
    print_rjcode(rjcode)
    if rjcode not in data:
        continue
    # path = data[rjcode]['Path']
    path = os.path.join(data['library_dir'], data[rjcode]['Path'])
    if not os.path.exists(path):
        continue
    playlist = ' '.join(find_audio_files(path))
    mpv = f'mpv --loop-playlist=no --no-video {playlist}'
    subprocess.call(shlex.split(mpv))
