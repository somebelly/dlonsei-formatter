# dlonsei-player
Use `mpv` to play some folders with RJcode in your local library.


# dlonsei-formatter
Format a folder with RJcode:
- Convert `'.wav'` files to `'.flac'`;
- Tag `'.flac'` and `'.mp3'` files using metadata from dlsite;
- Save `cover.jpg` in all subfolders which have audio files;
- Improve folder name readability.


## Dependences

[tqdm](https://github.com/tqdm/tqdm)

[ffmpeg-python](https://github.com/kkroening/ffmpeg-python)

[mutagen](https://github.com/quodlibet/mutagen)

[requests-html](https://github.com/psf/requests-html)

[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)

[pathvalidate](https://github.com/thombashi/pathvalidate)

[natsort](https://github.com/SethMMorton/natsort)

```
pip install tqdm ffmpeg-python mutagen requests-html beautifulsoup4 pathvalidate natsort
```

Note that `ffmpeg` and `mpv` should be available from the command line.


## Usage

Add to path (change `dlft` and `dlp` to whatever you like):
```
git clone https://github.com/somebelly/dlonsei-formatter.git
cd dlonsei-formatter
chmod +x dlonsei-formatter.py
chmod +x dlonsei-player.py
ln -s dlonsei-formatter.py <Somewhere in PATH/dlft>
ln -s dlonsei-player.py <Somewhere in PATH/dlp>
```

In a directory containing folders with RJcode:
```
dlft
```

Play some random folders:
```
dlp
```
or with some keywords:
```
dlp keyword1 keyword2 ...
```
E.g. (depending on your local library):
```
dlp 2017 癒し みもりあいの
```
will play
```
['RJ196614']
```



## References

[doujin_tagger](https://github.com/maybeRainH/doujin_tagger)

[Doujin_Voice_Renamer](https://github.com/Watanuki-Kimihiro/Doujin_Voice_Renamer)

[audio-converter](https://github.com/somebelly/audio-converter)
