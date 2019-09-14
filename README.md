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


## Usage

Add to path (change `dlft` to whatever you like):
```
git clone https://github.com/somebelly/dlonsei-formatter.git
cd dlonsei-formatter
chmod +x dlonsei-formatter.py
ln -s dlonsei-formatter.py <Somewhere in PATH/dlft>
```

In a directory containing folders with RJcode:
```
dlft
```
or indicate some folders on your own:
```
dlft -i <folder1 folder2 ...>
```


## References

[doujin_tagger](https://github.com/maybeRainH/doujin_tagger)

[Doujin_Voice_Renamer](https://github.com/Watanuki-Kimihiro/Doujin_Voice_Renamer)

[audio-converter](https://github.com/somebelly/audio-converter)
