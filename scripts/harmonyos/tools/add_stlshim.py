#!/usr/bin/env python3
"""Link libstlshim.so (see stlshim.cpp) into the extensions that need it.

Some clang-compiled C++ extensions reference std::bad_array_new_length's
complete-object constructor, which libstdc++ does not export; libstlshim.so
provides it. This script finds the offending ELF files under the given
directories and makes them depend on the shim.

Usage: add_stlshim.py <dir> [<dir> ...]
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
SHIM_DIR = os.path.join(HERE, "lib")
SHIM = "libstlshim.so"
MISSING = "_ZNSt20bad_array_new_lengthC1Ev"


def is_elf(path):
    try:
        with open(path, "rb") as f:
            return f.read(4) == b"\x7fELF"
    except OSError:
        return False


def undefined_symbols(path):
    out = subprocess.run(["nm", "-D", "--undefined-only", path],
                         capture_output=True, text=True).stdout
    return {ln.split()[-1] for ln in out.splitlines() if ln.split()}


def rpath_of(path):
    out = subprocess.run(["readelf", "-d", path], capture_output=True,
                         text=True).stdout
    for ln in out.splitlines():
        if ("(RPATH)" in ln or "(RUNPATH)" in ln) and "[" in ln:
            return ln.split("[", 1)[1].rstrip("]")
    return ""


def write_atomic(path, data):
    mode = os.stat(path).st_mode & 0o7777
    tmp = f"{path}.ohos-shim.{os.getpid()}.tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.chmod(tmp, mode)
    os.replace(tmp, path)


def main(targets):
    if not targets:
        print("usage: add_stlshim.py <dir> [<dir> ...]")
        return 2
    if not os.path.exists(os.path.join(SHIM_DIR, SHIM)):
        print(f"缺少 {SHIM_DIR}/{SHIM}")
        return 2
    patched = 0
    for root in targets:
        for dirpath, _dirs, files in os.walk(root):
            for fn in files:
                if not (fn.endswith(".so") or ".so." in fn):
                    continue
                path = os.path.join(dirpath, fn)
                if os.path.islink(path) or not is_elf(path):
                    continue
                if MISSING not in undefined_symbols(path):
                    continue

                data = open(path, "rb").read()
                if has_codesign_section(data):
                    write_atomic(path, bytes(strip_codesign(bytearray(data))[1]))
                os.chmod(path, 0o644)
                try:
                    subprocess.run([PATCHELF, "--add-needed", SHIM, path],
                                   check=False, capture_output=True)
                    rp = rpath_of(path)
                    parts = [p for p in rp.split(":") if p]
                    if SHIM_DIR not in parts:
                        parts.append(SHIM_DIR)
                    subprocess.run([PATCHELF, "--set-rpath", ":".join(parts), path],
                                   check=False, capture_output=True)
                finally:
                    os.chmod(path, 0o755)
                sign_file_atomic(path, force=True)
                patched += 1
                print(f"  已链接 shim: {os.path.relpath(path, root)}")
    print(f"共修补 {patched} 个扩展")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
