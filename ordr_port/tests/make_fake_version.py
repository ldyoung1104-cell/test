"""테스트용 가짜 새 버전 만들기: 난독화 이름을 모두 무작위로 바꾸고, 전역/함수를 끼워 넣고,
상수 몇 개를 바꾼다. 패치 프로그램이 이름 변경과 코드 이동을 견디는지 확인하는 용도.

    python tests/make_fake_version.py ref/2.323/base.j ref/2.323/mod.j 출력.j
"""
import random
import re
import string
import sys

sys.path.insert(0, __file__.rsplit("tests", 1)[0])
from jass_port import KEYWORDS, idents, is_obf, load, save  # noqa: E402


def main(base_p, mod_p, out_p, seed=2324):
    random.seed(seed)
    base, mod = load(base_p), load(mod_p)
    used = {n for l in base + mod for _, _, n in idents(l)}
    obf = sorted({n for l in base for _, _, n in idents(l) if is_obf(n)})
    chars = string.ascii_letters
    pool = [a + b + c for a in "QZXq" for b in chars for c in chars + string.digits]
    pool = [p for p in pool if p not in used and p not in KEYWORDS]
    random.shuffle(pool)
    m = dict(zip(obf, pool))

    def ren(l):
        out, last = [], 0
        for s, e, n in idents(l):
            out += [l[last:s], m.get(n, n)]
            last = e
        l = "".join(out) + l[last:]
        return re.sub(r'ExecuteFunc\("(\w+)"\)', lambda k: 'ExecuteFunc("%s")' % m.get(k.group(1), k.group(1)), l)

    fake = [ren(l).replace("2.323", "2.324") for l in base]
    gi = fake.index("globals")
    fake[gi + 1 : gi + 1] = ["integer ZZnew1=0", "boolean ZZnew2=false", "real array ZZnew3"]
    fidx = [i for i, l in enumerate(fake) if l.startswith("function ")]
    for at, body in sorted(
        [
            (fidx[3000], ["function ZZnewFunc takes nothing returns nothing", "set ZZnew1=ZZnew1+1", "endfunction"]),
            (fidx[1200], ["function ZZnewFunc2 takes integer ZZa returns integer", "return ZZa*2", "endfunction"]),
        ],
        reverse=True,
    ):
        fake[at:at] = body
    cnt = 0
    for i in range(0, len(fake), 997):
        if re.search(r"\b\d{2,}\b", fake[i]) and not fake[i].startswith("function"):
            fake[i] = re.sub(r"\b(\d{2,})\b", lambda k: str(int(k.group(1)) + 1), fake[i], count=1)
            cnt += 1
    save(out_p, fake)
    print("이름 %d개 변경, 상수 %d개 변경, %d줄" % (len(m), cnt, len(fake)))


if __name__ == "__main__":
    main(*sys.argv[1:4])
