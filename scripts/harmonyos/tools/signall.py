#!/usr/bin/env python3
"""Self-sign every unsigned ELF shared object under the given directories.

OpenHarmony enforces fs-verity code signing: a .so that has no .codesign
section cannot be dlopen()ed. Wheels from PyPI are therefore unusable until
they are signed, so run this after every `pip install`.

Usage: signall.py <dir> [<dir> ...]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from selfsign import has_codesign_section, sign_file_atomic  # noqa: E402


def is_elf(path):
    try:
        with open(path, "rb") as f:
            return f.read(4) == b"\x7fELF"
    except OSError:
        return False


def main(targets):
    if not targets:
        print("usage: signall.py <dir> [<dir> ...]")
        return 2
    total = signed = skipped = failed = 0
    for root in targets:
        for dirpath, _dirs, files in os.walk(root):
            for fn in files:
                if not (fn.endswith(".so") or ".so." in fn):
                    continue
                path = os.path.join(dirpath, fn)
                if os.path.islink(path) or not is_elf(path):
                    continue
                total += 1
                try:
                    if has_codesign_section(open(path, "rb").read()):
                        skipped += 1
                        continue
                    sign_file_atomic(path, force=False)
                    signed += 1
                except Exception as exc:  # noqa: BLE001
                    failed += 1
                    print(f"  失败 {path}: {exc}")
    print(f"ELF {total} | 新签名 {signed} | 已签名 {skipped} | 失败 {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
