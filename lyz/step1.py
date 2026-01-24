#! /usr/bin/env python3

import re
import sys
from os import path

THIS_PATH = path.dirname(path.abspath(__file__))
sys.path.insert(0, path.dirname(THIS_PATH))
from utils.aksara import split_aksara

SRC_FILES = ['0-src.txt', '1-src.txt', '2-src.txt']  # 原始文本，汉音行、梵文行交替
RE_INVALID = 'a-zāīūṛṝṭḍṅñṇṃśṣḥ|,!-', '\u3400-\u4DBF\u4e00-\u9fa5\U00020000-\U0002FA1F'
RE_PUNC = re.compile('[,!|]')
RE_GUNA = re.compile(r'\([' + RE_INVALID[1] + r']+\)')
RE_END_NUM = re.compile(r' *\(([一二三四五六七八九十百]+)\)$')
RE_END_HALF = re.compile(r'\([\u4e00-\u9fa5]\)$')
foley = {'寫': '思呀', '姪': '的呀'}
all_iast, all_hz, log_file = [], [], None
result = []


def print2(*args, sep=' ', show=True):
    text = sep.join(str(arg) for arg in args)
    show and print(text)
    log_file and log_file.write(text + '\n')


def scan():
    for fn in SRC_FILES:
        with open(path.join(THIS_PATH, fn), encoding='utf-8') as f:
            rows = f.read().strip().split('\n')
        if 0 and fn == '1-src.txt':  # 输出文本以便与 0-src.txt 比较改动
            txt_tmp = [re.sub('[()]', '', RE_END_NUM.sub('', r)) + (
                ' (' + RE_END_NUM.findall(r)[0] + ')' if RE_END_NUM.search(r) else '')
                       if re.match(r'^\d+', r) else r for r in rows]
            with open(path.join(THIS_PATH, '0-src-.txt'), 'w', encoding='utf-8') as f:
                f.write('\n'.join(txt_tmp))

        last_num, hz_txt, iast, hz_rs, iast_rs = 0, '', '', [], []

        for i, r in enumerate(rows):
            assert re.match(r'^(\d+\. |——|#\d|$)', r)  # 行首校验
            if re.match(r'^\d', r):
                m = re.search(r'^(\d+)\. (.+)', r)
                num, text = int(m.group(1)), m.group(2)  # 句序号，文本
                assert num == last_num or num == last_num + 1  # 每两行一组 地递增序号
                txt_tmp = RE_END_NUM.sub('', text)
                m = re.search('[^_() ' + RE_INVALID[0 if num == last_num else 1] + ']+', txt_tmp)
                assert not m, m and m.group()  # 检查非法字符
                if num == last_num + 1:  # 汉音行
                    hz_txt = txt_tmp
                    last_num = num
                    hz_rs.append(hz_txt)
                    if len(all_hz) == 2:
                        result.append(f'-[{num}]{hz_txt}')
                else:  # 梵文行
                    iast = text
                    assert hz_txt in rows[i - 1]  # 上一行是汉音行
                    assert len(re.split('[ -]', iast)) == len(hz_txt.split(' '))  # 汉字和梵文等量
                    iast_rs.append(iast)
            elif len(all_hz) == 2:
                result.append(r)
        all_iast.append(iast_rs)
        all_hz.append(hz_rs)


def cmp_src(cmp_iast=False, cmp_hz0=False, cmp_hz12=True, cmp_aksara=True):
    # 对比各步骤的梵文行，忽略所加的连字符'-'
    assert len(all_iast[0]) == len(all_iast[1]) == len(all_iast[2])  # 行数相同
    re_dash = re.compile('[,!|-]')
    print2('梵文0 vs 梵文1', show=cmp_iast)  # 除了连字符外，列出梵文及空格不一致处
    for i, (iast0, iast1) in enumerate(zip(all_iast[0], all_iast[1])):
        if re_dash.sub('', iast0) != re_dash.sub('', iast1):
            print2('梵0', i + 1, iast0, show=cmp_iast)
            print2('梵1', i + 1, iast1, show=cmp_iast)
    for i, (iast1, iast2) in enumerate(zip(all_iast[1], all_iast[2])):
        if re_dash.sub('', iast1) != re_dash.sub('', iast2):
            print2('梵1', i + 1, iast1, show=cmp_iast)
            print2('梵2', i + 1, iast2, show=cmp_iast)

    # 对比各步骤的汉音行（无末尾序号）
    assert len(all_hz[0]) == len(all_hz[1]) == len(all_hz[2]) == len(all_iast[0])
    re_bracket = re.compile('[_() ]')
    print2('字音0 vs 字音1', show=cmp_hz0)  # 除了括号和空格外，列出汉字不一致处，字应不变
    for i, (hz0, hz1) in enumerate(zip(all_hz[0], all_hz[1])):
        assert not re.search('[()]', hz0)  # 0-src 不含()
        if re_bracket.sub('', hz0) != re_bracket.sub('', hz1):
            print2('音0', i + 1, hz0, show=cmp_hz0)
            print2('音1', i + 1, hz1, show=cmp_hz0)

    print2('字音1 vs 字音2', show=cmp_hz12)
    for i, (hz1, hz2, iast1, iast2) in enumerate(zip(all_hz[1], all_hz[2], all_iast[1], all_iast[2])):
        assert RE_PUNC.sub('', iast1) == RE_PUNC.sub('', iast2), iast2
        if len(RE_GUNA.sub('□', hz1)) != len(RE_GUNA.sub('□', hz2)):
            print2('音1', i + 1, hz1, show=cmp_hz12)
            print2('音2', i + 1, hz2 or re.sub('[()]', '', hz2), show=cmp_hz12)

        aksaras = re.split('[ -]', iast2)
        hz1s, hz2s = hz1.split(' '), hz2.split(' ')
        assert len(aksaras) == len(hz1s) == len(hz2s)
        for c1, c2, iast in zip(hz1s, hz2s, aksaras):
            iast = split_aksara(re.sub('[,?!|]', '', iast))
            c1_len = len(RE_GUNA.sub('□', c1))
            if c1_len == len(iast) + 1 and RE_END_HALF.search(c2):
                c1_len -= 1
            if c1_len != len(iast):
                print2('音', i + 1, c1, c1_len, c2, ','.join(iast), show=cmp_aksara)

        item = ''.join(_gen_row(iast2, hz1s, hz2s))
        for ri, r in enumerate(result):
            m = r.startswith('-[') and re.search(r'-(\[\d+])(.+)$', r)
            if m:
                assert m.group(2) == hz2
                result[ri] = m.group(1) + item
                break


def _gen_row(iast1, hz1, hz2):
    item = []
    for iw, word in enumerate(re.split(' ', iast1)):
        if iw:
            item.append(' ')
        sub_words = re.split('-', word)
        for si, sub_word in enumerate(sub_words):
            c1, c2 = hz1.pop(0), hz2.pop(0)
            aksaras = split_aksara(sub_word)
            if si:
                item.append('-')
            for a in aksaras:
                item.append(a)
                if a not in ',?!|':
                    z1, c2 = _pick_hz_yin(c2)
                    z2, c1 = _pick_hz_yin(c1)
                    item.append(f'({z1}|{z2})')
    return item


def _pick_hz_yin(text):
    pos = 0
    if text[0] == '(':
        while text[pos] != ')':
            pos += 1
        return text[1:pos], text[pos+1:]
    return text[0], text[1:]


scan()

if __name__ == '__main__':
    import fire

    log_file = open(path.join(THIS_PATH, 'step1.log'), 'w', encoding='utf-8', buffering=1)
    fire.Fire(cmp_src)
    log_file.close()
    with open(path.join(THIS_PATH, 'step1.txt'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(result))
