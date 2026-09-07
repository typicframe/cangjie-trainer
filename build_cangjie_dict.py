# -*- coding: utf-8 -*-
from pathlib import Path
import json

SRC = Path(r'C:\\Users\\Administrator\\Documents\\Coding\\打字\\cj3_full.txt')
OUT = Path(r'C:\\Users\\Administrator\\Documents\\Coding\\打字\\cangjie3_dict.js')
REPORT = Path(r'C:\\Users\\Administrator\\Documents\\Coding\\打字\\cangjie_dict_report.txt')

# (code, preferred unicode codepoint)
CANTONESE = [
    ('raiu', 0x5605), ('rohf', 0x55BA), ('rkm', 0x5497), ('rhai', 0x5572), ('rmmr', 0x5514),
    ('kb', 0x5187), ('ohvf', 0x4FC2), ('oss', 0x4F62), ('rgpd', 0x54CB), ('rhhe', 0x569F),
    ('rtm', 0x5481), ('ridd', 0x561B), ('rwlg', 0x56C9), ('rtjs', 0x561E), ('rcl', 0x5416),
    ('rmvh', 0x5440), ('rbbr', 0x558E), ('rhdw', 0x5643), ('rkrd', 0x35CE), ('rwgn', 0x5622),
    ('rowr', 0x55F0), ('rsp', 0x5462), ('rdln', 0x5587), ('rjka', 0x556B), ('rmjk', 0x5649),
    ('rmy', 0x5413), ('rsmg', 0x5594), ('rmnr', 0x5475), ('rgg', 0x54C7), ('rkn', 0x54A6),
    ('rher', 0x54AF), ('rwg', 0x54E9), ('rggy', 0x5569), ('rtq', 0x54A9), ('pn', 0x4E5C),
    ('rici', 0x5692), ('romm', 0x564F), ('romq', 0x55F1), ('rpd', 0x5414), ('rjwj', 0x5513),
    ('ritf', 0x55FB), ('rite', 0x55A5), ('rnmp', 0x55BC), ('rtox', 0x56BF), ('rtjg', 0x56A1),
    ('rsmi', 0x565A), ('rhkp', 0x35AD), ('bucnh', 0x7747), ('yroip', 0x8AD7), ('buyrl', 0x7793),
    ('qwlg', 0x651E), ('qcno', 0x64B3), ('qjmo', 0x639F), ('qwot', 0x6435), ('qabt', 0x63FE),
    ('heyub', 0x9ED0), ('kbnl', 0x90C1), ('rmmfr', 0x8E0E), ('qdln', 0x63E6), ('qmre', 0x63FC),
    ('qjco', 0x6432), ('qvvv', 0x64F8), ('ndbuc', 0x5B6D), ('snlr', 0x5C59), ('qddf', 0x3A52),
    ('rkbl', 0x5590), ('rqyj', 0x551E), ('rumr', 0x5571), ('opmc', 0x50BE), ('qbbuu', 0x975A),
    ('rks', 0x53FB), ('ptwu', 0x61F5), ('boip', 0x814D), ('ftwv', 0x71F6), ('oiytk', 0x9938),
    ('bhdn', 0x8137), ('bang', 0x81B6), ('pdwyi', 0x4E78), ('bdd', 0x51A7), ('bu', 0x519A),
    ('ne', 0x6C39), ('rmsu', 0x5443), ('qlpb', 0x63F9), ('qndt', 0x63B9), ('qyta', 0x63DE),
    ('rmbsd', 0x8E2D), ('jjki', 0x8EDA), ('lhbt', 0x88C7), ('oapv', 0x5048), ('gylh', 0x57D7),
    ('thbu', 0x7740), ('vfii', 0x7DAB), ('jjyt', 0x282E2), ('rqbu', 0x210C1),
    ('yrttb', 0x8B1B), ('sgjwp', 0x807D), ('oiav', 0x98DF), ('oino', 0x98F2), ('yhe', 0x8FD4),
    ('hommn', 0x884C),
]

def parse_table(text):
    mapping = {}
    by_code = {}
    started = False
    for line in text.splitlines():
        line = line.strip()
        if line == '[DATA]':
            started = True
            continue
        if not started or not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        code, ch = parts[0].lower(), parts[1]
        if not code.isalpha():
            continue
        if ch not in mapping:
            mapping[ch] = code
        elif 'z' in mapping[ch] and 'z' not in code:
            mapping[ch] = code
        by_code.setdefault(code, []).append(ch)
    return mapping, by_code

def main():
    mapping, by_code = parse_table(SRC.read_text(encoding='utf-8'))
    wanted = []
    missing = []
    seen = set()
    for code, cp in CANTONESE:
        expected = chr(cp)
        chars = by_code.get(code, [])
        chosen = expected if expected in chars else (chars[0] if chars else None)
        if not chosen:
            missing.append('%s:%s' % (expected, code))
            continue
        if chosen in seen:
            continue
        seen.add(chosen)
        wanted.append((chosen, mapping[chosen]))
    payload = [
        '/* Cangjie 3 dictionary generated from Cangjie3-Plus (cj3.txt). */',
        'window.CANGJIE3_MAP = ' + json.dumps(mapping, ensure_ascii=False, separators=(',', ':')) + ';',
        'window.CANTONESE_SPOKEN_CHARS = ' + json.dumps([ch for ch, _ in wanted], ensure_ascii=False, separators=(',', ':')) + ';',
    ]
    OUT.write_text('\n'.join(payload) + '\n', encoding='utf-8')
    bmp = sum(1 for ch in mapping if len(ch) == 1 and 0x4E00 <= ord(ch) <= 0x9FFF)
    lines = [
        'unique_chars=%d' % len(mapping),
        'bmp_chars=%d' % bmp,
        'cantonese_found=%d' % len(wanted),
        'js_bytes=%d' % OUT.stat().st_size,
        'cantonese=' + ' '.join('%s:%s' % (ch, code) for ch, code in wanted),
        'missing=' + ' '.join(missing),
    ]
    REPORT.write_text('\n'.join(lines), encoding='utf-8')

if __name__ == '__main__':
    main()
