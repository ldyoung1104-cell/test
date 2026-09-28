"""2322 수정본에서 원하는 기능만 골라 2323 원본에 옮긴다 (1회용).

2322 원본이 없기 때문에, 2322 수정본에서 모드 줄을 지운 것을 '가상 2322 원본'으로 쓴다.
옮기는 기능은 모두 '순수 추가' 코드(새 함수/전역/호출)라서 이 방법이 정확하다.

사용법:
    python build_2323_from_2322.py 2322수정본.j 2323원본.j 출력.j
"""
import sys

from jass_port import load, port, save

# 2322 수정본 기준 줄 번호 (1부터, 끝 포함)
PORT = {
    "로또/위 전역": [(413, 420)],
    "자동조합 전역": [(2310, 2349)],
    "로또 함수": [(8346, 8481)],
    "@위/@취소 함수": [(62860, 62915)],
    "자동조합 함수": [(62930, 67653)],
    "자동조합 초기화 (main)": [(67668, 67669)],
    "@위 초기화 (main)": [(68106, 68106)],
    "로또 초기화 (main)": [(68108, 68108)],
}
# 옮기지 않는 추가 코드 (가상 원본/모드 양쪽에서 지움)
DROP = {
    "이지모드 전역": [(407, 412)],
    "자동로그인/스탯 변경": [(14960, 14982), (14986, 14986)],
    "복제맵 판정 무시": [(58381, 58385)],
    "치장 해제/이지모드 함수": [(62771, 62859), (62916, 62929)],
    "치장 해제/이지모드 호출 (main)": [(68105, 68105), (68107, 68107)],
}
# 2322 수정본 안에서 원본 줄을 '바꾼' 수정(무결성 검사 우회, 스킨 잠금 해제, 오라/날개 자동적용 제거,
# 도박 확률)은 원본을 알 수 없으므로 양쪽에 그대로 남겨 두어 옮겨지지 않게 한다.

EXPECT = {
    413: "boolean O30_LottoOn=false",
    2310: "player MyCurPlayer",
    8346: "function O30_LottoDraw",
    62860: "function O30_UpTick",
    62930: "function MyCraft",
    67668: 'call ExecuteFunc("MyInitData")',
    68106: "call O30_UpInit()",
    68108: "call O30_LottoInit()",
    407: "boolean O30_Easy=false",
    14960: "function O30_SetLoginStats",
    58381: 'if Ka=="맵 정보가 다른 복제맵입니다"',
    62771: "function O30_UnlockCosmetics",
    62916: "function O30_EasyInit",
    68105: "call O30_UnlockCosmetics()",
    68107: "call O30_EasyInit()",
}


def lines_of(spec):
    s = set()
    for ranges in spec.values():
        for a, b in ranges:
            s.update(range(a - 1, b))
    return s


def main(mod_path, new_path, out_path):
    a = load(mod_path)
    for ln, text in EXPECT.items():
        if not a[ln - 1].startswith(text):
            sys.exit("2322 파일이 예상과 다름: %d줄 '%s' 가 아님 -> '%s'" % (ln, text, a[ln - 1][:60]))
    port_l, drop_l = lines_of(PORT), lines_of(DROP)
    old_base = [l for i, l in enumerate(a) if i not in port_l and i not in drop_l]
    old_mod = [l for i, l in enumerate(a) if i not in drop_l]
    out, rep = port(old_base, old_mod, load(new_path))
    for h in rep["hunks"]:
        print("  hunk 2322 %s -> 2323 %s : %s" % (h["old_mod"], h["new_base"], h["preview"]))
    for w in rep["warnings"]:
        print("경고:", w)
    for e in rep["errors"]:
        print("오류:", e)
    save(out_path, out)
    print("저장:", out_path, "(%d줄)" % len(out))
    return 1 if rep["errors"] else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
