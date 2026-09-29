"""ORDR 자동 패치: 새 버전 맵에 우리 기능(자동조합, 로또, @위/@취소, 조합 도우미 UI 등)을 넣는다.

사용법 (파이썬 3.8 이상, 추가 설치 없음):
    python ordr_patch.py "ORDR_S2_2.324[C].w3x"
    python ordr_patch.py 새버전_war3map.j

결과 (입력 파일과 같은 폴더):
    ..._mod.w3x      기능이 들어간 맵 (입력이 w3x 이고 오류가 없을 때만)
    ..._mod.j        기능이 들어간 스크립트
    ..._report.txt   작업 보고서 (문제가 생기면 이 파일과 입력 맵을 Claude 에게 보내면 된다)

동작:
    ref/<버전>/base.j (그 버전 원본) 와 ref/<버전>/mod.j (그 버전 + 우리 기능) 의 차이를
    새 버전 스크립트로 옮긴다. 난독화 이름이 바뀌어도 줄 정렬로 이름 변환표를 만들어 맞춘다.
    성공하면 새 버전을 ref/<새버전>/ 에 저장해서 다음 버전은 그것을 기준으로 삼는다.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from jass_port import load, port, save  # noqa: E402
import mpq_pure  # noqa: E402

REF_DIR = os.path.join(HERE, "ref")


def lines_of(data):
    text = data.decode("utf-8-sig")
    return text.replace("\r\n", "\n").split("\n")


def map_version(lines):
    for l in lines:
        m = re.search(r'SetMapName\("[^"]*?(\d+\.\d+)', l)
        if m:
            return m.group(1)
    return None


def ver_key(v):
    return tuple(int(x) for x in re.findall(r"\d+", v))


def pick_ref(new_ver, forced):
    if forced:
        return forced
    vers = [
        d
        for d in os.listdir(REF_DIR)
        if os.path.exists(os.path.join(REF_DIR, d, "base.j")) and os.path.exists(os.path.join(REF_DIR, d, "mod.j"))
    ]
    if not vers:
        sys.exit("ref 폴더에 기준 파일이 없습니다.")
    vers.sort(key=ver_key)
    if new_ver:
        older = [v for v in vers if ver_key(v) <= ver_key(new_ver)]
        if older:
            return os.path.join(REF_DIR, older[-1])
    return os.path.join(REF_DIR, vers[-1])


def recipe_check(mod_lines, new_lines, rep):
    """자동조합 목록(MyAllKey)과 새 버전의 조합법 목록을 비교한다."""
    text_mod = "\n".join(mod_lines)
    keys = re.findall(r"^set MyAllKey\[\d+\]=\$([0-9A-F]{8})", text_mod, re.M)
    if not keys:
        return
    text_new = "\n".join(new_lines)
    m = re.search(r"^call (\w+)\(\$%s\)$" % keys[0], text_new, re.M)
    if not m:
        rep.append("경고: 새 버전에서 조합법 등록 코드를 찾지 못했습니다 (조합법 구조가 바뀌었을 수 있음)")
        return
    fn = m.group(1)
    new_keys = re.findall(r"^call %s\(\$([0-9A-F]{8})\)$" % fn, text_new, re.M)
    gone = sorted(set(keys) - set(new_keys))
    added = sorted(set(new_keys) - set(keys))
    rep.append("조합법: 자동조합 목록 %d개 / 새 버전 %d개" % (len(set(keys)), len(set(new_keys))))
    if gone:
        rep.append("경고: 새 버전에서 사라진 조합법 %d개 (자동조합 목록에는 남아 있음): %s" % (len(gone), " ".join(gone)))
    if added:
        rep.append(
            "경고: 새 버전에 새로 생긴 조합법 %d개 (자동조합 목록에는 아직 없음 -> Claude 에게 목록 갱신 요청): %s"
            % (len(added), " ".join(added))
        )


def pjass_check(base_path, out_path, rep):
    """pjass 가 있으면 문법 검사. 경고 목록이 원본과 같은지 비교한다."""
    tdir = os.environ.get("ORDR_PJASS_DIR", os.path.join(HERE, "tools"))
    exe = None
    for n in ("pjass.exe", "pjass"):
        p = os.path.join(tdir, n)
        if os.path.exists(p):
            exe = p
    cj, bj = os.path.join(tdir, "common.j"), os.path.join(tdir, "Blizzard.j")
    if not exe or not (os.path.exists(cj) and os.path.exists(bj)):
        rep.append("문법 검사(pjass): 도구가 없어 건너뜀")
        return

    def run(p):
        r = subprocess.run([exe, "+shadow", cj, bj, p], capture_output=True, text=True, errors="replace")
        msgs = sorted(re.sub(r"^[^:]*:\d+: ", "", l) for l in r.stdout.splitlines() if l.startswith(p + ":"))
        return ("Parse successful" in r.stdout and p in r.stdout.split("Parse successful")[-1]), msgs

    ok_b, m_b = run(base_path)
    ok_o, m_o = run(out_path)
    if ok_o and m_b == m_o:
        rep.append("문법 검사(pjass): 통과, 경고 목록이 원본과 같음")
    else:
        extra = [m for m in m_o if m not in m_b]
        rep.append("오류: 문법 검사(pjass) 실패 또는 새 경고 %d개: %s" % (len(extra), "; ".join(extra[:10])))


def main():
    ap = argparse.ArgumentParser(description="ORDR 새 버전 맵에 기능을 자동으로 넣습니다.")
    ap.add_argument("input", help="새 버전 맵(.w3x) 또는 war3map.j")
    ap.add_argument("--ref", help="기준 폴더 (기본: ref 안의 가장 가까운 버전)")
    ap.add_argument("--no-save-ref", action="store_true", help="성공해도 ref 에 새 버전을 저장하지 않음")
    args = ap.parse_args()

    t0 = time.time()
    src = args.input
    stem, ext = os.path.splitext(src)
    is_map = ext.lower() in (".w3x", ".w3m")
    print("입력:", src)
    if is_map:
        script_name, data = mpq_pure.read_script(src)
        print("  맵에서 %s 를 꺼냈습니다 (%d 바이트)" % (script_name, len(data)))
    else:
        script_name, data = "war3map.j", open(src, "rb").read()
    new_lines = lines_of(data)
    new_ver = map_version(new_lines)
    print("  맵 버전:", new_ver or "알 수 없음")

    ref = pick_ref(new_ver, args.ref)
    base = load(os.path.join(ref, "base.j"))
    mod = load(os.path.join(ref, "mod.j"))
    print("기준:", os.path.relpath(ref, HERE))

    if any(l.startswith(("function MyAcNode ", "function MyInitUi ")) for l in new_lines):
        sys.exit("\n이 맵에는 이미 자동조합 기능이 들어 있습니다. 공식 배포된 원본 맵을 넣어 주세요.")

    rep = ["ORDR 자동 패치 보고서", "입력: %s (버전 %s)" % (os.path.basename(src), new_ver), "기준: %s" % os.path.basename(ref), ""]
    if new_lines == base:
        print("입력이 기준 원본과 같습니다. 기준 수정본을 그대로 씁니다.")
        out, report = list(mod), {"hunks": [], "errors": [], "warnings": []}
    else:
        out, report = port(base, mod, new_lines, log=lambda *a: print(" ", *a))
    for h in report["hunks"]:
        rep.append("적용: 기준 %s -> 새 버전 %s : %s" % (h["old_mod"], h["new_base"], h["preview"]))
    recipe_check(mod, new_lines, rep)
    for w in report["warnings"]:
        rep.append("경고: " + w)
    for e in report["errors"]:
        rep.append("오류: " + e)

    out_j = stem + "_mod.j"
    save(out_j, out)
    base_tmp = stem + "_base.tmp.j"
    save(base_tmp, new_lines)
    pjass_check(base_tmp, out_j, rep)
    os.remove(base_tmp)

    errors = [l for l in rep if l.startswith("오류")]
    rep.append("")
    if errors:
        rep.append("결과: 오류 %d건. 맵은 만들지 않았습니다. 이 보고서와 입력 맵을 Claude 에게 보내 주세요." % len(errors))
    else:
        if is_map:
            out_map = stem + "_mod" + ext
            mpq_pure.write_script(src, out_map, script_name, "\r\n".join(out).encode("utf-8"))
            rep.append("결과: 성공 -> %s" % os.path.basename(out_map))
        else:
            rep.append("결과: 성공 -> %s" % os.path.basename(out_j))
        if new_ver and not args.no_save_ref and not os.path.exists(os.path.join(REF_DIR, new_ver)):
            d = os.path.join(REF_DIR, new_ver)
            os.makedirs(d)
            save(os.path.join(d, "base.j"), new_lines)
            shutil.copyfile(out_j, os.path.join(d, "mod.j"))
            rep.append("다음 버전 기준으로 ref/%s 를 저장했습니다." % new_ver)
    rep.append("걸린 시간: %.0f초" % (time.time() - t0))

    rep_path = stem + "_report.txt"
    open(rep_path, "w", encoding="utf-8").write("\n".join(rep) + "\n")
    print()
    print("\n".join(rep))
    print()
    print("보고서:", rep_path)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
