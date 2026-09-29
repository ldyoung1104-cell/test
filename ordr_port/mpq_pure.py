"""순수 파이썬 MPQ(w3x) 읽기/쓰기. 외부 라이브러리 불필요 (StormLib 대체).

지원 범위 (워크래프트 맵의 war3map.j 교체에 필요한 만큼):
- MPQ 포맷 v1 헤더, 암호화된 해시/블록 테이블
- 파일 읽기: 단일/섹터 분할, 파일 암호화, zlib/bzip2 압축
- 파일 교체: 새 데이터를 아카이브 끝에 zlib 로 붙이고 블록 테이블 항목만 바꾼다
  (해시 테이블은 그대로, 나머지 파일은 손대지 않음)
"""
import bz2
import struct
import zlib

MPQ_EXISTS = 0x80000000
MPQ_COMPRESS = 0x00000200
MPQ_IMPLODE = 0x00000100
MPQ_ENCRYPTED = 0x00010000
MPQ_FIX_KEY = 0x00020000
MPQ_SINGLE_UNIT = 0x01000000
MPQ_SECTOR_CRC = 0x04000000


def _crypt_table():
    t = [0] * 0x500
    seed = 0x00100001
    for i in range(0x100):
        idx = i
        for _ in range(5):
            seed = (seed * 125 + 3) % 0x2AAAAB
            a = (seed & 0xFFFF) << 16
            seed = (seed * 125 + 3) % 0x2AAAAB
            t[idx] = a | (seed & 0xFFFF)
            idx += 0x100
    return t


_T = _crypt_table()


def hash_string(s, typ):
    s1, s2 = 0x7FED7FED, 0xEEEEEEEE
    for c in s.upper().encode("latin-1"):
        s1 = (_T[typ * 0x100 + c] ^ (s1 + s2)) & 0xFFFFFFFF
        s2 = (c + s1 + s2 + (s2 << 5) + 3) & 0xFFFFFFFF
    return s1


def _decrypt(data, key):
    out = []
    s2 = 0xEEEEEEEE
    for (v,) in struct.iter_unpack("<I", data[: len(data) // 4 * 4]):
        s2 = (s2 + _T[0x400 + (key & 0xFF)]) & 0xFFFFFFFF
        x = v ^ ((key + s2) & 0xFFFFFFFF)
        out.append(x)
        key = ((((~key) << 0x15) + 0x11111111) & 0xFFFFFFFF) | (key >> 0x0B)
        s2 = (x + s2 + (s2 << 5) + 3) & 0xFFFFFFFF
    return out


def _encrypt(words, key):
    out = []
    s2 = 0xEEEEEEEE
    for x in words:
        s2 = (s2 + _T[0x400 + (key & 0xFF)]) & 0xFFFFFFFF
        out.append(x ^ ((key + s2) & 0xFFFFFFFF))
        key = ((((~key) << 0x15) + 0x11111111) & 0xFFFFFFFF) | (key >> 0x0B)
        s2 = (x + s2 + (s2 << 5) + 3) & 0xFFFFFFFF
    return struct.pack("<%dI" % len(out), *out)


def _decrypt_bytes(data, key):
    n = len(data) // 4 * 4
    words = _decrypt(data[:n], key)
    return struct.pack("<%dI" % len(words), *words) + data[n:]


def _decompress(buf, expected):
    if len(buf) >= expected:
        return buf[:expected]
    mask, body = buf[0], buf[1:]
    if mask == 0x02:
        return zlib.decompress(body)
    if mask == 0x10:
        return bz2.decompress(body)
    if mask == 0x12:
        return zlib.decompress(bz2.decompress(body))
    raise ValueError("지원하지 않는 압축 방식: 0x%02X" % mask)


class Archive:
    def __init__(self, path):
        self.path = path
        self.data = bytearray(open(path, "rb").read())
        self.off = self._find_header()
        d = self.data
        o = self.off
        (self.hsize, self.asize, self.ver, self.shift, self.ht_pos, self.bt_pos, self.ht_n, self.bt_n) = struct.unpack(
            "<IIHHIIII", d[o + 4 : o + 32]
        )
        self.sector = 512 << self.shift
        self.hash = _decrypt(bytes(d[o + self.ht_pos : o + self.ht_pos + self.ht_n * 16]), hash_string("(hash table)", 3))
        self.block = _decrypt(bytes(d[o + self.bt_pos : o + self.bt_pos + self.bt_n * 16]), hash_string("(block table)", 3))

    def _find_header(self):
        for off in range(0, len(self.data) - 32, 512):
            if self.data[off : off + 4] == b"MPQ\x1a":
                return off
        raise ValueError("MPQ 헤더를 찾을 수 없습니다 (w3x 맵 파일이 맞는지 확인)")

    def find(self, name):
        """name -> 블록 인덱스 (없으면 None)."""
        a, b = hash_string(name, 1), hash_string(name, 2)
        start = hash_string(name, 0) % self.ht_n
        for k in range(self.ht_n):
            e = (start + k) % self.ht_n
            n1, n2, loc, bi = self.hash[e * 4 : e * 4 + 4]
            if bi == 0xFFFFFFFF:
                return None
            if n1 == a and n2 == b and bi < self.bt_n:
                return bi
        return None

    def read(self, name):
        bi = self.find(name)
        if bi is None:
            return None
        fo, cs, fs, fl = self.block[bi * 4 : bi * 4 + 4]
        if fl & MPQ_IMPLODE:
            raise ValueError("PKWARE 압축 파일은 지원하지 않습니다: " + name)
        base = self.off + fo
        raw = bytes(self.data[base : base + cs])
        key = 0
        if fl & MPQ_ENCRYPTED:
            key = hash_string(name.replace("/", "\\").split("\\")[-1], 3)
            if fl & MPQ_FIX_KEY:
                key = ((key + fo) ^ fs) & 0xFFFFFFFF
        if fl & MPQ_SINGLE_UNIT:
            if fl & MPQ_ENCRYPTED:
                raw = _decrypt_bytes(raw, key)
            return _decompress(raw, fs) if fl & MPQ_COMPRESS else raw[:fs]
        if not fl & MPQ_COMPRESS:
            out = bytearray()
            for i in range(0, fs, self.sector):
                chunk = raw[i : i + self.sector]
                out += _decrypt_bytes(chunk, (key + i // self.sector) & 0xFFFFFFFF) if fl & MPQ_ENCRYPTED else chunk
            return bytes(out[:fs])
        n = (fs + self.sector - 1) // self.sector
        cnt = n + 1 + (1 if fl & MPQ_SECTOR_CRC else 0)
        tbl = raw[: cnt * 4]
        if fl & MPQ_ENCRYPTED:
            offs = _decrypt(tbl, (key - 1) & 0xFFFFFFFF)
        else:
            offs = list(struct.unpack("<%dI" % cnt, tbl))
        out = bytearray()
        for i in range(n):
            chunk = raw[offs[i] : offs[i + 1]]
            if fl & MPQ_ENCRYPTED:
                chunk = _decrypt_bytes(chunk, (key + i) & 0xFFFFFFFF)
            want = min(self.sector, fs - i * self.sector)
            out += _decompress(chunk, want)
        return bytes(out[:fs])

    def replace(self, name, content):
        """name 파일 내용을 content 로 바꾼다 (메모리 안에서). save() 로 저장."""
        bi = self.find(name)
        if bi is None:
            raise KeyError("맵 안에 %s 가 없습니다" % name)
        n = (len(content) + self.sector - 1) // self.sector
        sectors = []
        for i in range(n):
            chunk = content[i * self.sector : (i + 1) * self.sector]
            c = zlib.compress(chunk, 9)
            sectors.append(b"\x02" + c if len(c) + 1 < len(chunk) else chunk)
        offs = [(n + 1) * 4]
        for s in sectors:
            offs.append(offs[-1] + len(s))
        blob = struct.pack("<%dI" % (n + 1), *offs) + b"".join(sectors)
        # 아카이브 끝(파일 끝)에 붙인다
        pos = len(self.data)
        self.data += blob
        rel = pos - self.off
        if rel + len(blob) > 0xFFFFFFFF:
            raise ValueError("맵 파일이 너무 큽니다")
        self.block[bi * 4 : bi * 4 + 4] = [rel, len(blob), len(content), MPQ_EXISTS | MPQ_COMPRESS]
        enc = _encrypt(self.block, hash_string("(block table)", 3))
        o = self.off + self.bt_pos
        self.data[o : o + len(enc)] = enc
        self.asize = len(self.data) - self.off
        struct.pack_into("<I", self.data, self.off + 8, self.asize)

    def save(self, path):
        with open(path, "wb") as f:
            f.write(self.data)


def read_script(path):
    """w3x 에서 war3map.j 를 꺼낸다. (이름, 바이트) 반환."""
    a = Archive(path)
    for n in ("war3map.j", "scripts\\war3map.j", "Scripts\\war3map.j"):
        d = a.read(n)
        if d is not None:
            return n, d
    raise KeyError("맵 안에서 war3map.j 를 찾지 못했습니다")


def write_script(src_map, dst_map, name, content):
    a = Archive(src_map)
    a.replace(name, content)
    a.save(dst_map)
