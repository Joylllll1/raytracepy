#!/usr/bin/env python3
"""Link libmusl_compat.so into libraries that need symbols this libc lacks.

OpenHarmony's musl is missing a handful of functions that glibc-derived
binaries (and some wheel-vendored libraries, e.g. pillow's libzstd needing
qsort_r) expect. harmonybrew solves this with a small shim, musl-compat; this
script finds the ELF files whose undefined symbols are covered by that shim and
makes them depend on it.

Usage: fixcompat.py <dir> [<dir> ...]
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from selfsign import (  # noqa: E402
    has_codesign_section,
    sign_file_atomic,
    strip_codesign,
)

PATCHELF = "/data/service/hnp/bin/patchelf"
LOADER = "/lib/ld-musl-aarch64.so.1"
SHIM_DIR = os.path.join(HERE, "lib")
SHIM = "libmusl_compat.so"


def is_elf(path):
    try:
        with open(path, "rb") as f:
            return f.read(4) == b"\x7fELF"
    except OSError:
        return False


def dyn_syms(path, mode):
    try:
        out = subprocess.run(["nm", "-D", f"--{mode}-only", path],
                             capture_output=True, text=True).stdout
    except OSError:
        return set()
    res = set()
    for ln in out.splitlines():
        parts = ln.split()
        if parts:
            res.add(parts[-1].split("@")[0])
    return res


def needed(path):
    out = subprocess.run(["readelf", "-d", path], capture_output=True,
                         text=True).stdout
    return [ln.split("[")[1].rstrip("]") for ln in out.splitlines()
            if "(NEEDED)" in ln and "[" in ln]


def rpaths(path):
    out = subprocess.run(["readelf", "-d", path], capture_output=True,
                         text=True).stdout
    res = []
    for ln in out.splitlines():
        if ("(RPATH)" in ln or "(RUNPATH)" in ln) and "[" in ln:
            res += [p for p in ln.split("[", 1)[1].rstrip("]").split(":") if p]
    return res


def find_lib(soname, search_dirs):
    for d in search_dirs:
        if not d or not os.path.isdir(d):
            continue
        cand = os.path.join(d, soname)
        if os.path.exists(cand):
            return cand
        base = soname.split(".so")[0]
        try:
            entries = os.listdir(d)
        except OSError:
            continue
        for fn in entries:
            if fn.startswith(base + ".so"):
                return os.path.join(d, fn)
    return None


def write_atomic(path, data):
    mode = os.stat(path).st_mode & 0o7777
    tmp = f"{path}.ohos-compat.{os.getpid()}.tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.chmod(tmp, mode)
    os.replace(tmp, path)


def main(targets):
    if not targets:
        print("usage: fixcompat.py <dir> [<dir> ...]")
        return 2
    shim_path = os.path.join(SHIM_DIR, SHIM)
    if not os.path.exists(shim_path):
        print(f"缺少 {shim_path}")
        return 2

    libc = dyn_syms(LOADER, "defined")
    compat = dyn_syms(shim_path, "defined")
    print(f"libc 符号 {len(libc)} | musl-compat 符号 {len(compat)}")

    patched = 0
    for root in targets:
        for dirpath, _dirs, files in os.walk(root):
            for fn in files:
                if not (fn.endswith(".so") or ".so." in fn):
                    continue
                path = os.path.join(dirpath, fn)
                if os.path.islink(path) or not is_elf(path):
                    continue
                deps = needed(path)
                if SHIM in deps:
                    continue
                search = [dirpath] + [p.replace("$ORIGIN", dirpath)
                                      for p in rpaths(path)] + [SHIM_DIR]
                provided = set(libc)
                for dep in deps:
                    f = find_lib(dep, search)
                    if f:
                        provided |= dyn_syms(f, "defined")
                missing = dyn_syms(path, "undefined") - provided
                hit = missing & compat
                if not hit:
                    continue

                data = open(path, "rb").read()
                if has_codesign_section(data):
                    write_atomic(path, bytes(strip_codesign(bytearray(data))[1]))
                os.chmod(path, 0o644)
                try:
                    subprocess.run([PATCHELF, "--add-needed", SHIM, path],
                                   check=False, capture_output=True)
                    rp = rpaths(path)
                    if SHIM_DIR not in rp:
                        rp.append(SHIM_DIR)
                    subprocess.run([PATCHELF, "--set-rpath", ":".join(rp), path],
                                   check=False, capture_output=True)
                finally:
                    os.chmod(path, 0o755)
                sign_file_atomic(path, force=True)
                patched += 1
                print(f"  接入 musl-compat: {os.path.relpath(path, root)}"
                      f"  (缺 {len(hit)} 个符号, 如 {sorted(hit)[:3]})")
    print(f"共修补 {patched} 个 ELF")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
