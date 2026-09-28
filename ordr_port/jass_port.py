"""난독화된 war3map.j 사이에서 수정사항(모드)을 옮겨 주는 엔진.

3-way 방식:
    old_base  : 이전 버전 원본 j
    old_mod   : 이전 버전 + 모드 j
    new_base  : 새 버전 원본 j
    -> new_mod : 새 버전 + 모드 j

1. old_base 와 old_mod 를 정확히 비교해서 모드 hunk 를 뽑는다.
2. old_base 와 new_base 를, 짧은(난독화된) 식별자를 '#' 로 바꾼 뒤 줄 단위로 정렬한다.
3. 정렬이 같은 줄 쌍에서 식별자를 위치별로 짝지어 이름 변환표(예: uE -> uH)를 투표로 만든다.
   지역변수/인자는 함수별로 따로 투표한다.
4. 각 hunk 를 새 버전의 대응 위치에 넣고, hunk 안의 식별자를 변환표로 바꾼다.
5. 변환되지 않은 이름, 타입이 다른 이름, 이름 충돌 등을 검사해서 보고한다.
"""
import difflib
import re
from collections import Counter, defaultdict

KEYWORDS = set(
    "if then else elseif endif set call local function endfunction takes returns return "
    "nothing and or not null true false loop endloop exitwhen globals endglobals array "
    "constant native type extends code debug".split()
)
TYPES = set(
    "integer real boolean string handle code nothing agent event player widget unit destructable item "
    "ability buff force group trigger triggercondition triggeraction timer location region rect "
    "boolexpr sound conditionfunc filterfunc unitpool itempool race alliancetype racepreference "
    "gamestate igamestate fgamestate playerstate playerscore playergameresult unitstate aidifficulty "
    "eventid gameevent playerevent playerunitevent unitevent limitop widgetevent dialogevent "
    "unittype gamespeed gamedifficulty gametype mapflag mapvisibility mapsetting mapdensity "
    "mapcontrol minimapicon playerslotstate volumegroup camerafield camerasetup playercolor "
    "placement startlocprio raritycontrol blendmode texmapflags effect effecttype weathereffect "
    "terraindeformation fogstate fogmodifier dialog button quest questitem defeatcondition "
    "timerdialog leaderboard multiboard multiboarditem trackable gamecache version itemtype "
    "texttag attacktype damagetype weapontype soundtype lightning pathingtype mousebuttontype "
    "animtype subanimtype image ubersplat hashtable framehandle originframetype framepointtype "
    "textaligntype frameeventtype oskeytype abilityintegerfield abilityrealfield abilitybooleanfield "
    "abilitystringfield abilityintegerlevelfield abilityreallevelfield abilitybooleanlevelfield "
    "abilitystringlevelfield abilityintegerlevelarrayfield abilityreallevelarrayfield "
    "abilitybooleanlevelarrayfield abilitystringlevelarrayfield unitintegerfield unitrealfield "
    "unitbooleanfield unitstringfield unitweaponintegerfield unitweaponrealfield "
    "unitweaponbooleanfield unitweaponstringfield itemintegerfield itemrealfield itembooleanfield "
    "itemstringfield movetype targetflag armortype heroattribute defensetype regentype unitcategory "
    "pathingflag commandbuttoneffect".split()
)

# 문자열, 원시코드('A000'), 16진수, 숫자, 주석, 식별자
TOKEN_RE = re.compile(
    r'"(?:\\.|[^"\\])*"'
    r"|'[^']*'"
    r"|//.*$"
    r"|\$[0-9A-Fa-f]+|0[xX][0-9A-Fa-f]+"
    r"|\d+\.?\d*|\.\d+"
    r"|([A-Za-z_][A-Za-z0-9_]*)"
)
SHORT_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]{0,2}\b")
FUNC_RE = re.compile(r"^\s*(?:constant\s+)?function\s+([A-Za-z_]\w*)\s+takes\s+(.*?)\s+returns\s+(\w+)")
NATIVE_RE = re.compile(r"^\s*(?:constant\s+)?native\s+([A-Za-z_]\w*)\s+takes\s+(.*?)\s+returns\s+(\w+)")
LOCAL_RE = re.compile(r"^\s*local\s+(\w+)\s+(array\s+)?([A-Za-z_]\w*)")
GLOBAL_RE = re.compile(r"^\s*(?:constant\s+)?(\w+)\s+(array\s+)?([A-Za-z_]\w*)\s*(?:=|$)")


# common.j 에 있는 3글자 이하 네이티브 (난독화 이름 아님)
SHORT_NATIVES = set("I2S S2I I2R R2I R2S S2R Sin Cos Tan Pow And Or Not".split())


def is_obf(name):
    """난독화된 이름으로 볼지 여부 (1~3글자, 키워드/타입/네이티브 아님)."""
    return len(name) <= 3 and name not in KEYWORDS and name not in TYPES and name not in SHORT_NATIVES


def norm(line):
    return SHORT_RE.sub(lambda m: m.group(0) if not is_obf(m.group(0)) else "#", line)


def idents(line):
    """(시작, 끝, 이름) - 문자열/주석/원시코드 밖의 식별자만."""
    out = []
    for m in TOKEN_RE.finditer(line):
        if m.group(1):
            out.append((m.start(1), m.end(1), m.group(1)))
    return out


def load(path):
    data = open(path, "rb").read().decode("utf-8")
    return data.replace("\r\n", "\n").split("\n")


def save(path, lines):
    open(path, "wb").write("\r\n".join(lines).encode("utf-8"))


class Script:
    """j 파일의 구조 정보: 줄별 소속 함수, 함수 시그니처, 전역/지역 선언 타입."""

    def __init__(self, lines):
        self.lines = lines
        self.func_of = [None] * len(lines)
        self.funcs = {}  # name -> (takes, returns)
        self.globals = {}  # name -> "type" / "type array"
        self.locals = defaultdict(dict)  # func -> name -> type
        in_globals = False
        cur = None
        for i, l in enumerate(lines):
            s = l.strip()
            if s == "globals":
                in_globals = True
                continue
            if s == "endglobals":
                in_globals = False
                continue
            if in_globals:
                m = GLOBAL_RE.match(l)
                if m and m.group(1) not in KEYWORDS:
                    self.globals[m.group(3)] = m.group(1) + (" array" if m.group(2) else "")
                continue
            m = FUNC_RE.match(l)
            if m:
                cur = m.group(1)
                self.funcs[cur] = (self._sig(m.group(2)), m.group(3))
                for t, n in self._params(m.group(2)):
                    self.locals[cur][n] = t
            m = NATIVE_RE.match(l)
            if m:
                self.funcs[m.group(1)] = (self._sig(m.group(2)), m.group(3))
            self.func_of[i] = cur
            if cur:
                m = LOCAL_RE.match(l)
                if m:
                    self.locals[cur][m.group(3)] = m.group(1) + (" array" if m.group(2) else "")
            if s == "endfunction":
                cur = None

    @staticmethod
    def _params(takes):
        if takes.strip() == "nothing":
            return []
        out = []
        for p in takes.split(","):
            p = p.split()
            if len(p) == 2:
                out.append((p[0], p[1]))
        return out

    def _sig(self, takes):
        return tuple(t for t, _ in self._params(takes))

    def kind(self, name, func=None):
        """이름의 종류와 타입 (비교용)."""
        if func and name in self.locals.get(func, {}):
            return ("local", self.locals[func][name])
        if name in self.globals:
            return ("global", self.globals[name])
        if name in self.funcs:
            return ("func", self.funcs[name])
        return None


class Aligner:
    """old_base <-> new_base 정렬과 이름 변환표."""

    def __init__(self, old_lines, new_lines, log=print):
        self.old = Script(old_lines)
        self.new = Script(new_lines)
        self.log = log
        log("정렬 중... (%d줄 vs %d줄)" % (len(old_lines), len(new_lines)))
        sm = difflib.SequenceMatcher(
            None, [norm(x) for x in old_lines], [norm(x) for x in new_lines], autojunk=False
        )
        self.opcodes = sm.get_opcodes()
        self.line_map = {}
        for tag, i1, i2, j1, j2 in self.opcodes:
            if tag == "equal":
                for k in range(i2 - i1):
                    self.line_map[i1 + k] = j1 + k
        self._build_rename()

    def _build_rename(self):
        gvotes = defaultdict(Counter)
        lvotes = defaultdict(Counter)  # (old_func, name) -> Counter
        fvotes = defaultdict(Counter)  # old_func -> Counter(new_func)
        for i, j in self.line_map.items():
            a = idents(self.old.lines[i])
            b = idents(self.new.lines[j])
            if len(a) != len(b):
                continue
            fo, fn = self.old.func_of[i], self.new.func_of[j]
            if fo and fn:
                fvotes[fo][fn] += 1
            for (_, _, x), (_, _, y) in zip(a, b):
                if not is_obf(x) and not is_obf(y):
                    continue
                if fo and x in self.old.locals.get(fo, {}):
                    lvotes[(fo, x)][y] += 1
                else:
                    gvotes[x][y] += 1
        self.rename = {}
        self.rename_conf = {}
        for x, c in gvotes.items():
            y, n = c.most_common(1)[0]
            self.rename[x] = y
            self.rename_conf[x] = n / sum(c.values())
        self.local_rename = {k: c.most_common(1)[0][0] for k, c in lvotes.items()}
        self.func_map = {k: c.most_common(1)[0][0] for k, c in fvotes.items()}

    def map_insert_pos(self, i1, i2):
        """old_base 의 [i1,i2) 구간이 new_base 에서 어디인지. 못 찾으면 None."""
        if i2 > i1:
            js = [self.line_map.get(k) for k in range(i1, i2)]
            if None in js or js != list(range(js[0], js[0] + len(js))):
                return None
            return js[0], js[-1] + 1
        # 순수 삽입: 앞 줄 기준, 없으면 뒷 줄 기준
        if i1 - 1 in self.line_map:
            j = self.line_map[i1 - 1] + 1
            return j, j
        if i1 in self.line_map:
            j = self.line_map[i1]
            return j, j
        return None


class PortError(Exception):
    pass


def port(old_base, old_mod, new_base, log=print):
    """모드를 새 버전으로 옮긴다. (new_mod_lines, report) 반환."""
    al = Aligner(old_base, new_base, log)
    mod = Script(old_mod)
    report = {"hunks": [], "errors": [], "warnings": []}

    # 1. 모드 hunk 추출 (정확 비교)
    sm = difflib.SequenceMatcher(None, old_base, old_mod, autojunk=False)
    hunks = [op for op in sm.get_opcodes() if op[0] != "equal"]
    log("모드 hunk %d개" % len(hunks))

    # 모드가 새로 선언하는 이름 (변환 대상 아님)
    base_old = al.old
    mod_funcs = set(mod.funcs) - set(base_old.funcs)
    mod_globals = set(mod.globals) - set(base_old.globals)
    protected = mod_funcs | mod_globals
    for n in sorted(protected):
        if al.new.kind(n):
            report["errors"].append("이름 충돌: 모드가 선언한 '%s' 가 새 버전에도 이미 있음" % n)

    def translate(line, func):
        """old_mod 의 한 줄을 새 버전 이름으로 변환."""
        out = []
        last = 0
        for s, e, name in idents(line):
            new = name
            if name in protected:
                pass
            elif func in mod_funcs and name in mod.locals.get(func, {}):
                pass  # 모드 함수의 지역변수
            elif func and name in base_old.locals.get(func, {}):
                if (func, name) in al.local_rename:
                    new = al.local_rename[(func, name)]
                else:
                    report["warnings"].append("지역변수 변환 없음: %s.%s" % (func, name))
            elif name in al.rename:
                new = al.rename[name]
                k_old = base_old.kind(name)
                k_new = al.new.kind(new)
                if k_old and k_new and k_old != k_new:
                    report["errors"].append(
                        "타입 불일치: %s%s -> %s%s" % (name, k_old, new, k_new)
                    )
                elif al.rename_conf[name] < 0.9:
                    report["warnings"].append(
                        "확신도 낮음: %s -> %s (%.0f%%)" % (name, new, al.rename_conf[name] * 100)
                    )
            elif not is_obf(name):
                if base_old.kind(name) and not al.new.kind(name):
                    report["errors"].append("새 버전에 없는 이름: %s" % name)
            elif base_old.kind(name):
                report["errors"].append("변환표에 없는 이름: %s (새 버전에서 삭제됐을 수 있음)" % name)
            out.append(line[last:s])
            out.append(new)
            last = e
        out.append(line[last:])
        return "".join(out)

    # 2. hunk 를 새 버전 위치에 적용 (뒤에서부터)
    placed = []
    for tag, i1, i2, j1, j2 in hunks:
        pos = al.map_insert_pos(i1, i2)
        info = {
            "old_base": (i1 + 1, i2),
            "old_mod": (j1 + 1, j2),
            "preview": (old_mod[j1] if j2 > j1 else "(삭제) " + old_base[i1])[:80],
        }
        if pos is None:
            report["errors"].append(
                "위치를 못 찾음: old_base %d-%d 주변 코드가 새 버전에서 바뀜 -> 수동 확인 필요 (%s)"
                % (i1 + 1, i2, info["preview"])
            )
            continue
        new_lines = [translate(old_mod[k], mod.func_of[k]) for k in range(j1, j2)]
        info["new_base"] = (pos[0] + 1, pos[1])
        report["hunks"].append(info)
        placed.append((pos, new_lines))

    out = list(new_base)
    for (a, b), lines in sorted(placed, key=lambda p: p[0][0], reverse=True):
        out[a:b] = lines

    # 3. 결과 검증: 모드 줄에 쓰인 짧은 이름이 결과 파일에 선언돼 있는지
    res = Script(out)
    known = set(res.funcs) | set(res.globals)
    for (a, b), lines in placed:
        for l in lines:
            for _, _, n in idents(l):
                if is_obf(n) and n not in known and not any(n in d for d in res.locals.values()):
                    report["errors"].append("결과에 선언되지 않은 이름: %s  <- %s" % (n, l[:80]))
    report["errors"] = sorted(set(report["errors"]))
    report["warnings"] = sorted(set(report["warnings"]))
    return out, report
