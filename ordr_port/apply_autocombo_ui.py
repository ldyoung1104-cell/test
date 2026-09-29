"""이식된 j 파일의 자동조합 UI 를 mods/autocombo_ui.j 로 교체한다.

- 전역: 'integer MyUiPanel' ~ 'trigger MyChatCmdTrig' 구간 -> //#GLOBALS
- 함수: 'function MyUiRefreshGrid' ~ 'function MyAcSync' 끝 -> //#FUNCS
- 초기화: 'function MyInitUi' -> //#INIT
- 목록(MyAll*)에 없는 재료 유닛 아이콘은 맵의 CampaignUnitStrings.txt 에서 뽑아 넣는다.

사용법:
    python apply_autocombo_ui.py 입력.j 출력.j 맵.w3x
"""
import os
import re
import sys

from jass_port import load, save

HERE = os.path.dirname(os.path.abspath(__file__))


def sections(path):
    out, cur = {}, None
    for l in open(path, encoding="utf-8").read().replace("\r\n", "\n").split("\n"):
        m = re.match(r"^//#(\w+)$", l)
        if m and m.group(1) == "END":
            cur = None
        elif m and m.group(1) in ("GLOBALS", "FUNCS", "INIT"):
            cur = m.group(1)
            out[cur] = []
        elif cur:
            out[cur].append(l)
    return out


def find(lines, pred, start=0):
    for i in range(start, len(lines)):
        if pred(lines[i]):
            return i
    raise SystemExit("찾을 수 없음: %s" % pred.__doc__)


def func_end(lines, i):
    while lines[i].strip() != "endfunction":
        i += 1
    return i


def extra_icons(lines, map_path):
    import mpq

    mine = set(re.findall(r"set MyAllType\[\d+\]=\$([0-9A-F]{8})", "\n".join(lines)))
    mats = set(re.findall(r"call \w+\(\$554E4954,\$([0-9A-F]{8}),\d+\)", "\n".join(lines)))
    h = mpq.open_archive(map_path)
    txt = (mpq.read(h, "Units\\CampaignUnitStrings.txt") or b"").decode("utf-8", "replace")
    art, name = {}, {}
    for blk in re.split(r"\n(?=\[)", txt.replace("\r", "")):
        m = re.match(r"\[(\w{4})\]", blk)
        if not m:
            continue
        a = re.search(r"^Art=([^,\n]+)", blk, re.M)
        if a:
            art[m.group(1)] = a.group(1)
        n = re.search(r"^Name=(.+)$", blk, re.M)
        if n:
            # "|cff..해군 칼병|r - |cff..흔함|r" -> "해군 칼병"
            plain = re.sub(r"\|c[0-9a-fA-F]{8}|\|r", "", n.group(1)).split(" - ")[0].strip()
            if plain and '"' not in plain and "\\" not in plain:
                name[m.group(1)] = plain
    out = []
    for hx in sorted(mats - mine):
        uid = bytes.fromhex(hx).decode("latin-1")
        if uid in art:
            out.append('call SaveStr(MyUiMap,5,$%s,"%s")' % (hx, art[uid].replace("\\", "\\\\")))
        if uid in name:
            out.append('call SaveStr(MyUiMap,7,$%s,"%s")' % (hx, name[uid]))
    return out


def main(src, dst, map_path):
    L = load(src)
    sec = sections(os.path.join(HERE, "mods", "autocombo_ui.j"))

    # 초기화 함수 (뒤에서부터 바꿔야 줄 번호가 안 밀림)
    a = find(L, lambda l: l.startswith("function MyInitUi "))
    b = func_end(L, a)
    init = []
    for l in sec["INIT"]:
        if l == "//#EXTRA_ICONS":
            init.extend(extra_icons(L, map_path))
        else:
            init.append(l)
    L[a : b + 1] = init

    a = find(L, lambda l: l.startswith("function MyUiRefreshGrid "))
    b = func_end(L, find(L, lambda l: l.startswith("function MyAcSync "), a))
    L[a : b + 1] = sec["FUNCS"]

    a = find(L, lambda l: l == "integer MyUiPanel")
    b = find(L, lambda l: l == "trigger MyChatCmdTrig", a)
    L[a : b + 1] = sec["GLOBALS"]

    save(dst, L)
    print("저장:", dst, "(%d줄)" % len(L))


if __name__ == "__main__":
    main(*sys.argv[1:4])
