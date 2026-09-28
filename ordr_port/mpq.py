import ctypes, sys, os
L = ctypes.CDLL(os.environ.get("STORMLIB", "/tmp/claude-0/work/StormLib/build/libstorm.so"))
H = ctypes.c_void_p
L.SFileOpenArchive.argtypes=[ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(H)]
L.SFileOpenFileEx.argtypes=[H, ctypes.c_char_p, ctypes.c_uint, ctypes.POINTER(H)]
L.SFileGetFileSize.argtypes=[H, ctypes.POINTER(ctypes.c_uint)]; L.SFileGetFileSize.restype=ctypes.c_uint
L.SFileReadFile.argtypes=[H, ctypes.c_void_p, ctypes.c_uint, ctypes.POINTER(ctypes.c_uint), ctypes.c_void_p]
L.SFileCloseFile.argtypes=[H]; L.SFileCloseArchive.argtypes=[H]
L.SFileHasFile.argtypes=[H, ctypes.c_char_p]
L.SFileAddFileEx.argtypes=[H, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint]
L.SFileRemoveFile.argtypes=[H, ctypes.c_char_p, ctypes.c_uint]
L.SFileCompactArchive.argtypes=[H, ctypes.c_char_p, ctypes.c_bool]
L.SFileFlushArchive.argtypes=[H]
def open_archive(p, readonly=True):
    h=H()
    if not L.SFileOpenArchive(p.encode(), 0, 0x100 if readonly else 0, ctypes.byref(h)):
        raise OSError("open failed %s err=%d"%(p, ctypes.get_errno()))
    return h
def read(h, name):
    f=H()
    if not L.SFileOpenFileEx(h, name.encode(), 0, ctypes.byref(f)): return None
    n=L.SFileGetFileSize(f, None); buf=ctypes.create_string_buffer(n); got=ctypes.c_uint()
    L.SFileReadFile(f, buf, n, ctypes.byref(got), None); L.SFileCloseFile(f)
    return buf.raw[:got.value]
def write(h, name, data, tmp):
    open(tmp,'wb').write(data)
    if L.SFileHasFile(h, name.encode()): L.SFileRemoveFile(h, name.encode(), 0)
    # MPQ_FILE_COMPRESS|MPQ_FILE_REPLACEEXISTING, zlib
    ok=L.SFileAddFileEx(h, tmp.encode(), name.encode(), 0x200|0x80000000, 0x02, 0x02)
    if not ok: raise OSError("add failed "+name)
if __name__=="__main__":
    cmd=sys.argv[1]
    if cmd=="get":
        h=open_archive(sys.argv[2]); d=read(h, sys.argv[3])
        if d is None: sys.exit("not found")
        open(sys.argv[4],'wb').write(d); print(len(d))
    elif cmd=="put":
        h=open_archive(sys.argv[2], False); write(h, sys.argv[3], open(sys.argv[4],'rb').read(), sys.argv[4]+".tmp")
        L.SFileFlushArchive(h); L.SFileCloseArchive(h); os.remove(sys.argv[4]+".tmp"); print("ok")
