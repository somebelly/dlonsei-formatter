# pylint: disable=W0702,W0703

import os
import shutil
import re
import json
from time import localtime
from datetime import date

import ffmpeg
import mutagen
from mutagen.easyid3 import EasyID3
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from tqdm import tqdm
from pathvalidate import sanitize_filepath

local_data = os.path.expanduser('~/.dlonsei_data.json')
session = HTMLSession()

if not os.path.exists(local_data):
    with open(local_data, 'w+') as f:
        f.write("{}")
with open(local_data, 'r+') as f:
    data = json.load(f)
    if 'library_dir' not in data:
        data['library_dir'] = os.getcwd()

tags = {
    'Organization': 'maker_name',
    'Illustrator': 'イラスト',
    'Lyricist': 'シナリオ',
    'Date': '販売日',
    'Artist': '声優',
    'Author': '作者',
    'Content rating': '年齢指定',
    'Genre': '作品形式',
    'Original format': 'ファイル形式',
    'Album': 'work_name',
    'Tags': 'ジャンル',
    'Series': 'シリーズ名',
    'Event': 'イベント',
}

for k in [
        'Content rating',
        'Original format',
        'Tags',
        'Series',
        'Year',
        'Illustrator',
        'Event',
]:
    EasyID3.RegisterTXXXKey(k, k)

brackets = '()[]{}<>【】『』「」（）'


def opposite_of(bracket):
    index = brackets.find(bracket)
    if index % 2 == 0:
        return brackets[index + 1]
    return brackets[index - 1]


def get_relative_path_of(rjcode, folder=None):
    if folder is not None:
        y, m = localtime(os.path.getmtime(folder))[:2]
    else:
        y = date.today().year
        m = date.today().month
    yy = str(y)
    if m < 10:
        mm = "0" + str(m)
    else:
        mm = str(m)
    _date = yy + mm

    return os.path.join(_date, rjcode)


def get_path_of(rjcode, folder=None):
    _relative_path = get_relative_path_of(rjcode, folder)
    return os.path.join(data['library_dir'], _relative_path)


def save_to_local():
    with open(local_data, 'r+') as _f:
        _f.seek(0)
        json.dump(data, _f, indent=4, ensure_ascii=False)
        _f.truncate()


def exist_in_library(rjcode):
    return os.path.exists(get_path_of(rjcode))


def get_rjcode(_str):
    try:
        return re.findall(r"(RJ\d{6})", _str)[0]
    except:
        return ''


def get_audio_info(file):
    try:
        _data = mutagen.File(file)
        sample_rate = _data.info.sample_rate
        bitrate = _data.info.bitrate
        return (sample_rate, bitrate)
    except Exception as e:
        print(e)
        return ()


def ffmpeg_run(_input,
               _output,
               in_options=None,
               out_options=None,
               run_options=None):
    in_options = in_options or {}
    out_options = out_options or {}
    run_options = run_options or {}

    if 'loglevel' not in out_options:
        out_options['loglevel'] = 'warning'
    if 'map_metadata' not in out_options:
        out_options['map_metadata'] = -1
    if 'overwrite_output' not in run_options:
        run_options['overwrite_output'] = True
    audio = ffmpeg.input(_input, **in_options).audio
    # print(ffmpeg.output(audio, output, **out_options).compile())
    ffmpeg.output(audio, _output, **out_options).run(**run_options)


def acflac(file, compression_level=5, replace=True):
    out_options = {'compression_level': compression_level}

    try:
        ffmpeg_run(file, '.Noname.flac', out_options=out_options)
        title = os.path.splitext(file)[0]
        if replace:
            os.remove(file)
        # while os.path.exists(title + '.flac'):
        #     title += '_flac'
        shutil.move('.Noname.flac',
                    sanitize_filepath(title + '.flac', platform="auto"))
    except Exception as e:
        print(e)


def a2webm(file, bit_rate='320k', replace=True):
    out_options = {'audio_bitrate': bit_rate}
    if file.lower().endswith('.webm'):
        out_options = {'c': 'copy'}

    ffmpeg_run(file, '.Noname.webm', out_options=out_options)
    title = os.path.splitext(file)[0]
    if replace:
        os.remove(file)
    # while os.path.exists(title + '.webm'):
    #     title += '_webm'
    shutil.move('.Noname.webm',
                sanitize_filepath(title + '.webm', platform="auto"))


def acwebm(file, bit_rate='320k', replace=True):
    try:
        a2webm(file, bit_rate=bit_rate, replace=replace)
    except:
        try:
            a2webm(file, bit_rate='256k', replace=replace)
        except Exception as e:
            print(e)


def remove_metadata(file, replace=True):
    ext = os.path.splitext(file)[1]
    new = f'.Noname{ext}'
    ffmpeg_run(file, new, out_options={'c': 'copy'})
    # title = os.path.splitext(file)[0]
    if replace:
        os.remove(file)
    # while os.path.exists(title + '.webm'):
    #     title += '_webm'
    shutil.move(new, sanitize_filepath(file, platform="auto"))


def got_metadata(rjcode):
    return rjcode in data


def get_dl_count(rjcode, current=False):
    global session

    if rjcode not in data:
        get_metadata(rjcode)

    if (not current) and ('dl_count' in data[rjcode]):
        return data[rjcode]['dl_count']

    url = f"https://www.dlsite.com/maniax/work/=/product_id/{rjcode}.html"

    try:
        page = session.get(url)
        page.html.render()
        dl_count = page.html.find("._dl_count")[0].text
        # Prevent connection closed error.
        session.close()
        session = HTMLSession()
    except:
        return ''

    data[rjcode]['dl_count'] = dl_count

    return dl_count


def get_metadata(rjcode):
    if rjcode in data:
        return data[rjcode]

    metadata = {}
    url = f"https://www.dlsite.com/maniax/work/=/product_id/{rjcode}.html"

    try:
        page = session.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
    except:
        data[rjcode] = metadata
        return {}

    if page.status_code == 404:
        data[rjcode] = metadata
        return {}

    def get_text(html):
        text = ' '.join(html.find_all(text=True)).strip().replace("/", " ")
        return ' '.join(text.split())

    extract = soup.select("#work_outline")
    info_name = [get_text(text) for text in extract[0].select("th")]
    info_attr = [get_text(text) for text in extract[0].select("td")]
    metadata = dict(zip(info_name, info_attr))
    metadata['work_name'] = get_text(soup.select("#work_name")[0])
    metadata['maker_name'] = get_text(soup.select(".maker_name")[0])
    metadata['img'] = 'https:' + soup.find(
        class_="slider_item active").select("img")[0].get('src')

    data[rjcode] = metadata
    return metadata


def tag(file):
    rjcode = get_rjcode(file)
    metadata = get_metadata(rjcode)

    if not metadata:
        return

    # ext = os.path.splitext(file)[1].lower()
    audio = mutagen.File(file, easy=True)

    audio.delete()
    if audio.tags is None:
        audio.add_tags()

    for _k in tags:
        if tags[_k] in metadata:
            audio[_k] = metadata[tags[_k]]
    audio['Title'] = os.path.split(os.path.splitext(file)[0])[1]
    if tags['Date'] in metadata:
        audio['Year'] = metadata[tags['Date']][:4]

    audio.save()


def has_cover(folder, exts=None):
    exts = exts or ['.jpg', '.webp']
    paths = [os.path.join(folder, 'cover' + ext) for ext in exts]
    try:
        for path in paths:
            if os.path.exists(path):
                return True
    except:
        pass
    return False


def get_cover(rjcode):
    metadata = get_metadata(rjcode)
    try:
        return session.get(metadata['img']).content
    except:
        return b''


def cover(folder, img=b''):
    if not has_cover(folder):
        if not img:
            img = get_cover(get_rjcode(folder))
            if not img:
                return
        open(os.path.join(folder, 'cover.jpg'), 'wb').write(img)


def find_audio_files_in(_dir, exts=None):
    exts = exts or ['.mp3', '.flac']
    return [
        os.path.join(root, file) for ext in exts
        for root, dirs, files in os.walk(_dir) for file in files
        if file.lower().endswith(ext)
    ]


def find_folders_with_rjcode_in(_dir):
    if get_rjcode(_dir):
        return [_dir]
    return [
        os.path.join(root, folder) for root, dirs, files in os.walk(_dir)
        for folder in dirs if get_rjcode(folder)
    ]


def find_folders_with_audio_files_in(_dir, exts=None):
    exts = exts or ['.mp3', '.flac']
    return list(
        dict.fromkeys([
            os.path.split(file)[0]
            for file in find_audio_files_in(_dir, exts=exts)
        ]))


def format_title(title):
    temp = title
    for _str in re.findall(r"(【.*?】)", title):
        temp = temp.replace(_str, '')
    if temp[0] in '『「':
        return temp[1:temp.find(opposite_of(temp[0]))].strip()
    if '』' in temp:
        return temp[:temp.find('』') + 1].strip()
    if '」' in temp:
        return temp[:temp.find('」') + 1].strip()
    return temp.strip()


def format_artist(artist):
    temp = artist.split()
    if len(temp) > 4:
        temp = temp[:4]
        temp.append('他')
    temp = ' '.join(temp)
    for _str in re.findall(r"(（.*?）)", temp):
        temp = temp.replace(_str, '')
    return temp.strip()


def get_formatted_name_of(rjcode,
                          template='{RJcode} [{Circle}] {Title} ({Artist})',
                          _dict=None):
    _dict = _dict or {}
    metadata = get_metadata(rjcode)
    _dict['RJcode'] = rjcode
    try:
        _dict['Circle'] = metadata[tags['Organization']]
    except:
        _dict['Circle'] = ''
    try:
        _dict['Title'] = format_title(metadata[tags['Album']])
    except:
        _dict['Title'] = ''
    try:
        _dict['Artist'] = format_artist(metadata[tags['Artist']])
    except:
        _dict['Artist'] = ''
    temp = template.format_map(_dict)
    temp = temp.replace('()', '')
    temp = temp.replace('[]', '')
    return temp.strip()


def formatter(_dir=os.getcwd(), **kwargs):
    print('\rIndexing...', end='')
    folders = find_folders_with_rjcode_in(_dir)
    print('Finished.')

    bar = tqdm(folders,
               bar_format='{l_bar}{bar}{{{n_fmt}/{total_fmt}{postfix}}}',
               dynamic_ncols=True)

    for folder in bar:
        rjcode = get_rjcode(folder)
        bar.set_description(rjcode)
        get_metadata(rjcode)

        if kwargs['convert']:
            if kwargs['lossy']:
                exts_to_convert = ['.wav', '.aif', '.flac']
            else:
                exts_to_convert = ['.wav', '.aif']

            to_convert = find_audio_files_in(folder, exts=exts_to_convert)
            now = 0
            for _f in to_convert:
                bar.set_postfix_str('Converting...' + str(now) + '/' +
                                    str(len(to_convert)))
                if kwargs['lossy']:
                    acwebm(_f)
                else:
                    acflac(_f)
                now += 1

        if not kwargs['metadata']:
            exts_to_convert = ['.mp3']
            to_convert = find_audio_files_in(folder, exts=exts_to_convert)
            for _f in to_convert:
                bar.set_postfix_str('Removing metadata...' + str(now) + '/' +
                                    str(len(to_convert)))
                remove_metadata(_f)
                now += 1

        if kwargs['force'] or not got_metadata(rjcode):
            if get_metadata(
                    rjcode) and kwargs['tag_files'] and not kwargs['lossy']:
                to_tag = find_audio_files_in(folder)
                now = 0
                for _f in to_tag:
                    bar.set_postfix_str('Tagging...' + str(now) + '/' +
                                        str(len(to_tag)))
                    tag(_f)
                    now += 1

        if kwargs['save_cover']:
            to_cover = find_folders_with_audio_files_in(folder)
            img = get_cover(rjcode)
            for _f in to_cover:
                cover(_f, img)

        _new_name = get_relative_path_of(rjcode, folder=folder)

        data[rjcode]['Path'] = _new_name
        shutil.move(folder, _new_name)
        save_to_local()
        bar.set_postfix_str('Finished.')


def scanner(_dir=os.getcwd()):
    print('\rIndexing...', end='')
    folders = find_folders_with_rjcode_in(_dir)
    print('Finished.')

    _bar = tqdm(folders,
                bar_format='{l_bar}{bar}{{{n_fmt}/{total_fmt}{postfix}}}',
                dynamic_ncols=True)

    for folder in _bar:
        rjcode = get_rjcode(folder)
        _bar.set_description(rjcode)
        get_metadata(rjcode)
        data[rjcode]['Path'] = os.path.relpath(folder,
                                               start=data['library_dir'])
        _bar.set_postfix_str('Finished.')

    save_to_local()
