#! /usr/bin/env python3
"""
从原始 mp3 文件、lrc歌词文件生成词和句的音频文件
python3 split_mp3.py <mp3_file> <folder/prefix> [--options]
"""
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from os import path, makedirs
import shutil
import pylrc
import re


def de_silencer(audio, filename, mode=1):
    parts = detect_nonsilent(audio, min_silence_len=250, silence_thresh=-40) if mode else []
    if parts:
        if len(parts) > 1 and mode > 1:  # 无声部分都拆开以便检查相邻几个音属于一个词及时刻范围，以便准确拆词
            out_path, fn = path.dirname(filename), path.basename(filename)
            for i, (start_t, end_t) in enumerate(parts):
                audio[start_t:end_t].export(out_path + '/' + fn[:4] + '-%02d-%d-%d ' % (
                    i, start_t, end_t) + fn[4:], format='mp3')
            return
        start_t, end_t = parts[0][0], parts[-1][1]  # 去除词首尾的无声部分，这样lrc中的时刻允许有偏差
        audio = audio[start_t:end_t]
    audio.export(filename, format='mp3')


def split_mp3(mp3_file, out_dir_prefix='', merge_sentence=False, join_ln=' ',
              only_i=0, mp3_with_text=False, de_silence=1, rebuild=False,
              start_i=0, st_i=500):
    """
    从原始 mp3 文件、lrc歌词文件生成词和句的音频文件
    :param mp3_file: 原始 mp3 文件
    :param out_dir_prefix: 输出目录及词音频文件前缀，例如 '../mp3/heart_m/h'，缺省同源文件的目录
    :param merge_sentence: 是否合并生成句音频，是则需要在lrc中某些行末有标点 '|'或'||'，有'||'时自动为True
    :param join_ln: 合并句文本时的连接字符，n表示换行
    :param only_i: 仅生成指定序号的词音频，用于微调某个词的时刻位置
    :param mp3_with_text: 生成的词音频文件是否带iast转写，便于试听检查
    :param de_silence: 是否去除词的无声部分，0-按lrc时刻拆分，1-去除词首尾的无声部分，2-无声部分都拆开以便拆词
    :param rebuild: 是否全部重新生成，默认仅生成缺少的音频
    :param start_i: 词音频文件的起始序号
    :param st_i: 句音频文件的起始序号
    """
    if not path.exists(mp3_file):
        return print('skip ' + mp3_file)
    mp3_with_text = mp3_with_text or de_silence > 1
    with open(mp3_file[:-3] + 'lrc', encoding='utf-8') as f:
        content = f.read()
        merge_sentence = False if merge_sentence in ['no', 'not'] else \
            merge_sentence or '||' in content
        if merge_sentence and 'n' in join_ln:
            join_ln = '\n'
        assert not merge_sentence or '|' in content
        lrc = pylrc.parse(content)
    song = AudioSegment.from_mp3(mp3_file)
    content, sentence, voc_i = [], [], start_i
    print(lrc.title, len(lrc), 'rows')

    if not out_dir_prefix:
        r = path.basename(mp3_file)
        out_dir_prefix = mp3_file[:-4] + '/' + (r[0] if re.match('^[a-z]', r) else 'a')
    if rebuild:
        shutil.rmtree(path.dirname(out_dir_prefix), True)
    makedirs(path.dirname(out_dir_prefix), exist_ok=True)

    start_st, st_voc_n = 0, 0
    text_st, ab = '', ''
    st_end, indent = False, False
    af = ['a', 'b', 'c', 'd', 'e', 'f']
    for i_, r in enumerate(lrc[:-1]):  # lrc末行有时刻无文本
        start = round(r.time * 1000)  # 开始时刻，毫秒
        end = round(lrc[i_ + 1].time * 1000)  # 结束时刻，毫秒
        if re.match(r'^\s?\d{2}', r.text):  # mp3_to_lrc.py 的结果未改默认文本
            text0 = text = r.text = re.search(r'\s?(\d+)', r.text).group(1)
        else:
            r.text = re.sub(r'\d+-\d+|\d{4}', '', re.sub(r'\d+\.mp3', '?', r.text))
            text0 = re.sub(r'^ |\s+$', '', r.text)
            text = re.sub(r'\s*[,!:.\d|-]*$|^\s*--.*$', '', text0)
        text_ext = text0[len(text):]

        if not r.text.strip():  # 遇到空行结束，忽略后面可能的重复内容
            break
        if not text or text.startswith('['):  # 行内容为“-”或[内容]则跳过
            continue
        if text.startswith('.'):  # 中途需要拆词时，在多出的行中“[time]. ”加点标记编号不变，以免打乱后续文件名
            text = text[1:].strip()
            voc_i -= 1
        if merge_sentence:
            text_st += text + join_ln
            start_st = 0 if '◆' in text else start_st or start
            st_end = re.search(r'\|\|', r.text) and not re.search(r'^\|\|', r.text)
        voc_i += 1
        st_voc_n += 1
        text_fn = re.sub(r'[A-Z]', lambda m: m.group().lower(), text.replace("'", 'a'))
        print(voc_i, start, end - start, text + text_ext,
              f' ▷{st_i}' if st_end and st_voc_n > 1 else '',
              '' if merge_sentence or text_fn == text else text_fn)

        if r.text.startswith('='):  # 相邻两行词文本相同，就不增加编号
            voc_i -= 1
            text = text.replace('=', '').strip()
        elif r.text.startswith('.'):  # 加点标记编号不变，文件名数字后加abc等子名
            assert ab, f'invalid sub-num: {r.text}'
            ab = af[af.index(ab) + 1]
        else:
            ab = 'a' if lrc[i_ + 1].text.startswith('.') else ''

        if not only_i or voc_i in range(only_i - 4, only_i + 5):
            if not merge_sentence and end - start > 1500:
                end -= 100
            out_fn = out_dir_prefix + '%02d%s.mp3' % (
                voc_i, ' ' + re.sub('[/:*?"<>|]', '', text[:20]).strip() if mp3_with_text else ab)
            if voc_i == only_i or rebuild or not path.exists(out_fn):
                de_silencer(song[start:end], out_fn, de_silence)
            if ' ' not in text_fn and len(text_fn.split('-')) < 3 and \
                    de_silence == 1 and not path.exists(f'voc/{text_fn}.mp3'):
                if text_fn not in ['e', 'na', 'sā', 'yā']:
                    makedirs('voc', exist_ok=True)
                    shutil.copy(out_fn, f'voc/{text_fn}.mp3')

        sentence.append(text + ('▷%02d%s' % (voc_i, ab)) + text_ext + (
            f' ▷{st_i}' if st_end and st_voc_n > 1 else ''))
        if st_end:
            if not only_i and de_silence < 2 and st_voc_n > 1:
                assert start_st
                out_fn = out_dir_prefix + '%d%s.mp3' % (
                    st_i, ' ' + text_st[:20].strip() if mp3_with_text else '')
                if not path.exists(out_fn):
                    song[start_st:end].export(out_fn, format='mp3')
            start_st, st_i, text_st, st_voc_n = 0, st_i + 1, '', 0

        if re.search(r'[,.|]\s*$', r.text):  # 如果行末有句点，就合并前面各行内容
            for j, s in enumerate(sentence[:-1]):
                if '◆' in s:
                    sentence[j] = '\n' + sentence[j] + '\n'
                elif '\n' in join_ln or not s.endswith('-'):
                    sentence[j] += join_ln
            if indent:
                sentence[0] = '  ' + sentence[0]
            row = ''.join(sentence)
            indent = ', ▷' in row
            content.append(re.sub(r', ▷\d+[a-f]?', lambda m: m.group()[1:], row))
            sentence = []

    print(out_dir_prefix + '.txt')
    with open(out_dir_prefix + '.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join((content or []) + sentence).strip())


if __name__ == '__main__':
    import fire

    fire.Fire(split_mp3)
