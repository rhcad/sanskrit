"""
Convert audio or video files to mp3 format
Usage:
python3 audio2mp3.py <input_path> --ext=wav
python3 audio2mp3.py <input_file>
python3 audio2mp3.py --help
"""
from os import path
import subprocess
from glob import glob


def to_mp3(in_fn, output_path):
    out_fn = path.join(output_path, path.basename(in_fn)[:-3] + 'mp3')
    if not path.exists(out_fn):
        subprocess.call('ffmpeg -i ' + in_fn + ' ' + out_fn, shell=True)


def ffmpeg_audio_to_mp3(input_path='.', output_path='', ext='wma'):
    """
    Convert audio or video files to mp3 format
    :param {str} input_path: audio path (need ext parameter) or filename
    :param {str} output_path: output path, default as folder path of input file
    :param {str} ext: extension such as 'wav', 'wma', 'mp4'
    """
    if path.isfile(input_path):
        to_mp3(input_path, output_path or path.dirname(input_path))
    else:
        for file in glob(path.join(input_path, '*.' + ext)):
            to_mp3(file, output_path or input_path)


if __name__ == '__main__':
    import fire
    fire.Fire(ffmpeg_audio_to_mp3)
