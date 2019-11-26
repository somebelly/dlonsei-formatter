import os, shutil
import re, json
import ffmpeg, mutagen
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


def get_path_of(rjcode):
    return sanitize_filepath(
        os.path.join(data['library_dir'], get_formatted_name_of(rjcode)))


def save_to_local():
    with open(local_data, 'r+') as f:
        f.seek(0)
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.truncate()


def exist_in_library(rjcode):
    return os.path.exists(get_path_of(rjcode))


def get_rjcode(str):
    try:
        return re.findall(r"(RJ\d{6})", str)[0]
    except:
        return ''


def get_audio_info(file):
    try:
        data = mutagen.File(file)
        sample_rate = data.info.sample_rate
        bitrate = data.info.bitrate
        return (sample_rate, bitrate)
    except Exception as e:
        print(e)
        return ()


def acflac(file, compression_level=5, replace=True):
    try:
        ffmpeg.input(file).output('.Noname.flac',
                                  loglevel="quiet",
                                  compression_level=compression_level).run()
        title = os.path.splitext(file)[0]
        if replace:
            os.remove(file)
        # while os.path.exists(title + '.flac'):
        #     title += '_flac'
        shutil.move('.Noname.flac', sanitize_filepath(title + '.flac'))
    except Exception as e:
        print(e)


def acwebm(file, bit_rate=320, replace=True):
    try:
        sample_rate, rate_old = get_audio_info(file)
        if rate_old > bit_rate * 1e3:
            ba = str(bit_rate) + 'k'
        else:
            ba = str(int(rate_old / 1e3)) + 'k'
        ffmpeg.input(file).output('.Noname.webm',
                                  loglevel="quiet",
                                  audio_bitrate=ba).run()
        title = os.path.splitext(file)[0]
        if replace:
            os.remove(file)
        # while os.path.exists(title + '.webm'):
        #     title += '_webm'
        shutil.move('.Noname.webm', sanitize_filepath(title + '.webm'))
    except Exception as e:
        print(e)


def got_metadata(rjcode):
    return (rjcode in data)


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

    data[rjcode] = metadata

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


def has_cover(folder, exts=['.jpg', '.webp']):
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


def find_audio_files_in(dir, exts=['.mp3', '.flac']):
    return [
        os.path.join(root, file) for ext in exts
        for root, dirs, files in os.walk(dir) for file in files
        if file.lower().endswith(ext)
    ]


def find_folders_with_rjcode_in(dir):
    if get_rjcode(dir):
        return [dir]
    return [
        os.path.join(root, folder) for root, dirs, files in os.walk(dir)
        for folder in dirs if get_rjcode(folder)
    ]


def find_folders_with_audio_files_in(dir, exts=['.mp3', '.flac']):
    return list(
        dict.fromkeys([
            os.path.split(file)[0]
            for file in find_audio_files_in(dir, exts=exts)
        ]))


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


def format(dir=os.getcwd(),
           convert=True,
           save_cover=True,
           force=False,
           tag_files=True,
           lossy=False):
    print('\rIndexing...', end='')
    folders = find_folders_with_rjcode_in(dir)
    print('Finished.')

    bar = tqdm(folders,
               bar_format='{l_bar}{bar}{{{n_fmt}/{total_fmt}{postfix}}}',
               dynamic_ncols=True)

    for folder in bar:
        rjcode = get_rjcode(folder)
        bar.set_description(rjcode)

        if convert:
            if lossy:
                to_convert = find_audio_files_in(
                    folder, exts=['.wav', '.aif', '.flac'])
            else:
                to_convert = find_audio_files_in(folder, exts=['.wav', '.aif'])
            now = 0
            for f in to_convert:
                bar.set_postfix_str('Converting...' + str(now) + '/' +
                                    str(len(to_convert)))
                if lossy:
                    acwebm(f)
                else:
                    acflac(f)
                now += 1

        if force or not got_metadata(rjcode):
            if get_metadata(rjcode) and tag_files:
                to_tag = find_audio_files_in(folder)
                now = 0
                for f in to_tag:
                    bar.set_postfix_str('Tagging...' + str(now) + '/' +
                                        str(len(to_tag)))
                    tag(f)
                    now += 1

        if save_cover:
            to_cover = find_folders_with_audio_files_in(folder)
            img = get_cover(rjcode)
            # now = 0
            for f in to_cover:
                # bar.set_postfix_str('Saving cover...' + str(now) + '/' +
                #                     str(len(to_cover)))
                cover(f, img)
                # now += 1

        folder_name = get_formatted_name_of(rjcode)
        shutil.move(
            folder,
            sanitize_filepath(
                os.path.join(os.path.split(folder)[0], folder_name)))
        bar.set_postfix_str('Finished.')
