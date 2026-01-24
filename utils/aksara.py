import re

RE_AKSARA_VOWEL = re.compile(r'[aiuāīūṛṝḷḹáíúeēèoōò]+[ṃḥ]?', re.I)
RE_AKSARA_PUNC_NUM = re.compile(r'\s+|[▷,?!:]|\|+\d[|\d.-]*|\|+|\d[\d.-]*|'
                                r'[\u4e00-\u9fa5]+|[\uFF01-\uFF5E\u3000-\u303F()♪]+')
RE_AKSARA_TYPE_NUM = re.compile(r'[\d०-९]')
RE_AKSARA_HZ_PUNC = re.compile(r'[\uFF01-\uFF5E\u3000-\u303F]')
RE_AKSARA_HZ = re.compile(r'[\u4e00-\u9fa5]')
RE_N_CON = re.compile('^[ṅñṇnm][kgcjtdṭḍpb]')
END_CONS = 'kgtdnrṛṝṭḍṅñṇnmṃśṣḥsh'


def split_aksara(data):
    items = []

    def split_str(text):
        ret = []
        while text:
            vowel_match = RE_AKSARA_VOWEL.search(text)
            if vowel_match is None:
                ret.append(text)
                items.append(text)  # consonant
                break
            vowel_index = vowel_match.start()
            vowel = vowel_match.group()
            syllable = text[:vowel_index + len(vowel)]
            if RE_N_CON.match(syllable) and items and RE_AKSARA_VOWEL.match(items[-1][-1]):
                items[-1] += syllable[0]
                syllable = syllable[1:]
            items.append(syllable)  # has vowel
            ret.append(syllable)
            text = text[vowel_index + len(vowel):]
        return ret

    def merge_end(item):
        if len(item) > 1 and RE_AKSARA_VOWEL.match(item[-2][-1]) and item[-1] in END_CONS:
            item[-2] += item[-1]
            item.pop()

    idx = 0
    for sentence in RE_AKSARA_PUNC_NUM.split(data):
        if len(split_str(sentence)) > 1:
            merge_end(items)
        idx += len(sentence)
        punc = data[idx] if idx < len(data) else ''
        if idx < len(data):
            if re.search(r'[|\d\s\u4e00-\u9fa5\uFF01-\uFF5E\u3000-\u303F]', data[idx]):
                if punc == '|':
                    re_pattern = re.compile(r'[|\d.-]')
                elif RE_AKSARA_TYPE_NUM.match(punc):
                    re_pattern = re.compile(r'[\d.-]')
                elif re.match(r'\s', punc):
                    re_pattern = re.compile(r'\s')
                elif RE_AKSARA_HZ.match(punc):
                    re_pattern = RE_AKSARA_HZ
                else:
                    re_pattern = RE_AKSARA_HZ_PUNC
                while idx + 1 < len(data) and re_pattern.match(data[idx + 1]):
                    punc += data[idx + 1]
                    idx += 1
            items.append(punc)
            idx += 1

    return items


if __name__ == '__main__':
    test_data = 'Aśanamā yanta,canabhājane| vajra-paṇe||'
    result = split_aksara(test_data)
    assert result == ['A', 'śa', 'na', 'mā', ' ', 'yan', 'ta', ',', 'ca', 'na', 'bhā',
                      'ja', 'ne', '|', ' ', 'va', 'jra', '-pa', 'ṇe', '||']
    print(result)
