"""
Split mp3 file into word files and lrc text file
Usage:
python3 mp3_to_lrc.py <mp3_file>
python3 mp3_to_lrc.py --help
"""
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from os import path, makedirs
import shutil
import re


def split_mp3(mp3_file, min_silence_len=80, silence_thresh=-40):
    """
    Split mp3 file into word files and lrc text file
    :param mp3_file: the source mp3 file
    :param min_silence_len: the minimum length for any silent section in milliseconds
    :param silence_thresh: the upper bound for how quiet is silent in dFBS
    """
    audio = AudioSegment.from_mp3(mp3_file)
    parts = detect_nonsilent(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)  # dBFS
    out_path = mp3_file[:-4]
    shutil.rmtree(out_path, True)
    makedirs(out_path, exist_ok=True)

    file_title = path.basename(mp3_file)[:-4]
    lrc_rows = [f'[ti: {file_title}]',
                f'[00:00.000] [ti: {file_title}]']
    lrc_file = out_path + '.lrc'
    print(f'{len(parts)} non-silent segments detected, {lrc_file}')
    for i, (start_t, end_t) in enumerate(parts):
        if i > 0:
            lrc_rows.append(ms_to_time(parts[i-1][1]) + '------ %04d' % (start_t - parts[i-1][1]))
        audio[start_t:end_t].export(path.join(out_path, '%02d.mp3' % i), format='mp3')
        lrc_rows.append(ms_to_time(start_t) + '%02d.mp3 %04d %d-%d' % (i, end_t - start_t, start_t, end_t))

    lrc_rows.append(ms_to_time(len(audio)))
    with open(lrc_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lrc_rows))


def ms_to_time(ms):
    return '[%02d:%02d.%03d] ' % (ms // 60000, ms // 1000 % 60, ms % 1000)


if __name__ == '__main__':
    import fire

    fire.Fire(split_mp3)
