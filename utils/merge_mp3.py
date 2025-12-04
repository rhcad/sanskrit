#! /usr/bin/env python3
from pydub import AudioSegment
from glob import glob
from os import path


def merge_mp3(src_path, dest_file=''):
    """
    Merge mp3 files in src_path into a mp3 file (dest_file).
    :param src_path: the source direction with mp3 files
    :param dest_file: target mp3 filename, empty to test source files
    """
    files = sorted(glob(path.join(str(src_path), '*.mp3')))
    result = None
    print(f'{len(files)} mp3 files in {src_path}')
    for fn in files:
        audio = AudioSegment.from_mp3(fn)
        if dest_file:
            result = result + audio if result else audio
        else:
            print(path.basename(fn), len(audio) / 1000)
    if result:
        print(dest_file, len(result) / 1000)
        result.export(dest_file, format='mp3')


if __name__ == '__main__':
    import fire

    fire.Fire(merge_mp3)
