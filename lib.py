import ffmpeg
import mutagen
from mutagen.easyid3 import EasyID3
import shutil
import os
import re
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import json
from tqdm import tqdm

local_data = os.path.expanduser('~/.dlonsei_data.json')

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


def init():
    if not os.path.exists(local_data):
        with open(local_data, 'w+') as f:
            f.write("{}")


def get_rjcode(str):
    try:
        return re.findall(r"(RJ\d{6})", str)[0]
    except:
        return ''


def acflac(file, compression_level=5, replace=True):
    try:
        ffmpeg.input(file).output('.Noname.flac',
                                  loglevel="quiet",
                                  compression_level=compression_level).run()
        title = os.path.splitext(file)[0]
        if replace:
            os.remove(file)
        while os.path.exists(title + '.flac'):
            title += '_flac'
        shutil.move('.Noname.flac', title + '.flac')
    except Exception as e:
        print(e)


def get_metadata(rjcode):
    with open(local_data) as f:
        data = json.load(f)
    if rjcode in data:
        return data[rjcode]

    metadata = {}
    url = f"https://www.dlsite.com/maniax/work/=/product_id/{rjcode}.html"

    try:
        page = HTMLSession().get(url)
        soup = BeautifulSoup(page.content, "html.parser")
    except:
        return {}

    if page.status_code == 404:
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

    with open(local_data, 'r+') as f:
        data = json.load(f)
        data[rjcode] = metadata
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

    return metadata


def tag(file):
    rjcode = get_rjcode(file)
    metadata = get_metadata(rjcode)

    if not metadata:
        return

    ext = os.path.splitext(file)[1].lower()
    audio = mutagen.File(file, easy=True)

    audio.delete()
    if audio.tags is None:
        audio.add_tags()

    for k in tags.keys():
        if tags[k] in metadata:
            audio[k] = metadata[tags[k]]
    audio['Title'] = os.path.split(os.path.splitext(file)[0])[1]
    if tags['Date'] in metadata:
        audio['Year'] = metadata[tags['Date']][:4]

    audio.save()


def find_audio_files_in(dir, exts=['.mp3', '.flac']):
    return [
        os.path.join(root, file) for ext in exts
        for root, dirs, files in os.walk(dir) for file in files
        if file.lower().endswith(ext)
    ]


def get_folders_with_rjcode_in(dir):
    return [
        os.path.join(root, folder) for root, dirs, files in os.walk(dir)
        for folder in dirs if get_rjcode(folder)
    ]


def format_title(title):
    temp = title
    for str in re.findall(r"(【.*?】)", title):
        temp = temp.replace(str, '')
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
    for str in re.findall(r"(（.*?）)", temp):
        temp = temp.replace(str, '')
    return temp.strip()


def get_formatted_name_of(rjcode,
                          template='{RJcode} [{Circle}] {Title} ({Artist})',
                          dict={}):
    metadata = get_metadata(rjcode)
    dict['RJcode'] = rjcode
    try:
        dict['Circle'] = metadata[tags['Organization']]
    except:
        dict['Circle'] = ''
    try:
        dict['Title'] = format_title(metadata[tags['Album']])
    except:
        dict['Title'] = ''
    try:
        dict['Artist'] = format_artist(metadata[tags['Artist']])
    except:
        dict['Artist'] = ''
    temp = template.format_map(dict)
    temp = temp.replace('()', '')
    temp = temp.replace('[]', '')
    return temp.strip()


def format(dir=os.getcwd(), convert=True):
    folders = get_folders_with_rjcode_in(dir)

    bar = tqdm(folders,
               bar_format='{l_bar}{bar}{{{n_fmt}/{total_fmt}{postfix}}}',
               dynamic_ncols=True)

    for folder in bar:
        rjcode = get_rjcode(folder)
        bar.set_description(rjcode)

        if convert:
            to_convert = find_audio_files_in(folder, exts=['.wav'])
            now = 0
            for f in to_convert:
                bar.set_postfix_str('Converting...' + str(now) + '/' +
                                    str(len(to_convert)))
                acflac(f)
                now += 1

        if get_metadata(rjcode):
            to_tag = find_audio_files_in(folder)
            now = 0
            for f in to_tag:
                bar.set_postfix_str('Tagging...' + str(now) + '/' +
                                    str(len(to_tag)))
                tag(f)
                now += 1

        folder_name = get_formatted_name_of(rjcode)
        shutil.move(folder,
                    os.path.join(os.path.split(folder)[0], folder_name))
        bar.set_postfix_str('Finished.')
