#!/usr/bin/env python3
"""Bring wheel-installed packages into a usable state on OpenHarmony.

Runs the three fixes in the right order:
  1. fixwheels  - libc soname rewrite, libpython linkage, code signing
  2. fixcompat  - link musl-compat for symbols this libc is missing
  3. fixwheels  - re-sign whatever fixcompat touched

Usage: fixall.py <site-packages> [<dir> ...]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import fixcompat  # noqa: E402
import fixwheels  # noqa: E402


def main(targets):
    if not targets:
        print("usage: fixall.py <site-packages> [<dir> ...]")
        return 2
    print("== 1/3 修补 ELF 链接与签名 ==")
    rc = fixwheels.main(targets)
    print("== 2/3 接入 musl-compat ==")
    fixcompat.main(targets)
    print("== 3/3 重新签名 ==")
    fixwheels.main(targets)
    print("完成")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
