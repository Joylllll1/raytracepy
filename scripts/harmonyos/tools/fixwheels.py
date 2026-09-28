#!/usr/bin/env python3
"""Make wheel-installed extension modules usable on OpenHarmony.

PyPI musllinux wheels are built for a normal musl distro. On OpenHarmony two
things have to be repaired before the modules can be imported, both of which
are pure ELF bookkeeping:

1. They link against `libc.musl-aarch64.so.1`, but this host's loader is named
   `libc.so`. Left alone, musl loads the loader a *second* time as a plain
   library and symbol resolution breaks.  -> --replace-needed
2. They rely on the interpreter's symbols being globally visible, which this
   musl does not provide for dlopen()ed objects.  -> --add-needed libpython
3. Every ELF needs an fs-verity `.codesign` section or dlopen() is denied.

patchelf cannot edit a file that already carries a `.codesign` section, so the
signature is stripped first and re-applied at the end.

Usage: fixwheels.py <site-packages> [<dir> ...]
"""
import os
import subprocess
import sys
import sysconfig

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from selfsign import (  # noqa: E402
    has_codesign_section,
    sign_file_atomic,
    strip_codesign,
)

PATCHELF = "/data/service/hnp/bin/patchelf"
OLD_LIBC = "libc.musl-aarch64.so.1"
NEW_LIBC = "libc.so"

# the shared libpython that extension modules must be linked against
_LDLIB = sysconfig.get_config_var("LDLIBRARY") or (
    f"libpython{sys.version_info.major}.{sys.version_info.minor}.so")
# LDLIBRARY may carry a path; keep the basename and drop a leading "lib" for a
# soname-style name only when it already looks like one
PY_SONAME = os.path.basename(_LDLIB)

EXT_SUFFIX = sysconfig.get_config_var("EXT_SUFFIX") or ""


def is_elf(path):
    try:
        with open(path, "rb") as f:
            return f.read(4) == b"\x7fELF"
    except OSError:
        return False


def needed(path):
    try:
        out = subprocess.run(["readelf", "-d", path], capture_output=True,
                             text=True).stdout
    except OSError:
        return []
    return [ln.split("[")[1].rstrip("]") for ln in out.splitlines()
            if "(NEEDED)" in ln and "[" in ln]


def is_extension_module(fn):
    if EXT_SUFFIX and fn.endswith(EXT_SUFFIX):
        return True
    return ".abi3.so" in fn or ".cpython-" in fn


def write_atomic(path, data):
    mode = os.stat(path).st_mode & 0o7777
    tmp = f"{path}.ohos-fix.{os.getpid()}.tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.chmod(tmp, mode)
    os.replace(tmp, path)


def fix_file(path):
    """Return one of: 'patched', 'signed', 'skipped'."""
    changed = False
    data = open(path, "rb").read()
    signed = has_codesign_section(data)
    if signed:
        # patchelf refuses to touch a signed ELF
        _, data = strip_codesign(bytearray(data))
        write_atomic(path, bytes(data))
        data = bytes(data)
        changed = True

    deps = needed(path)
    os.chmod(path, 0o644)
    try:
        if OLD_LIBC in deps:
            subprocess.run([PATCHELF, "--replace-needed", OLD_LIBC, NEW_LIBC, path],
                           check=False, capture_output=True)
            changed = True
        if is_extension_module(os.path.basename(path)) and PY_SONAME not in deps:
            subprocess.run([PATCHELF, "--add-needed", PY_SONAME, path],
                           check=False, capture_output=True)
            changed = True
    finally:
        os.chmod(path, 0o755)

    sign_file_atomic(path, force=True)
    return "patched" if changed else "signed"


def main(targets):
    if not targets:
        print("usage: fixwheels.py <site-packages> [<dir> ...]")
        return 2
    stats = {"patched": 0, "signed": 0}
    failed = 0
    for root in targets:
        for dirpath, _dirs, files in os.walk(root):
            for fn in files:
                if not (fn.endswith(".so") or ".so." in fn):
                    continue
                path = os.path.join(dirpath, fn)
                if os.path.islink(path) or not is_elf(path):
                    continue
                try:
                    stats[fix_file(path)] += 1
                except Exception as exc:  # noqa: BLE001
                    failed += 1
                    print(f"  失败 {path}: {exc}")
    print(f"修补 {stats['patched']} | 仅重签 {stats['signed']} | 失败 {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
