#!/usr/bin/env python3
"""Install the HarmonyOS PC dependency set for RayTracePy.

Target runtime: the official "HarmonyOS-ified" CPython 3.12.9 published by the
OpenHarmony PC Developer community (platform ``ohos-aarch64``, target triple
``aarch64-unknown-linux-ohos``).  Install it first::

    curl -fsSL https://gitcode.com/OpenHarmonyPCDeveloper/cmd-pkgs/releases/download/pkgs/install-python.sh | sh -s -- 3.12.9

Then, from a venv created with that interpreter::

    <venv>/bin/python scripts/install_dependencies_harmonyos.py

Why this is not just ``pip install -r``:

* ``--prefer-binary`` is required.  The community index carries the OHOS wheels,
  but the extra index (Tsinghua / PyPI) offers newer source distributions that
  would otherwise shadow them -- matplotlib then fails to build (no meson).
* dask must stay out.  datashader 0.19 no longer needs it, dask 2023.x breaks on
  Python 3.12, and current dask pulls pyarrow.
* numpy stays below 2.0 because the sources still use ``np.trapz``.

Verified on the target device (2026-10-10): import OK, ``pytest`` 7 passed, the
official example exits 0, and the 3M-ray reference load is bit-identical to the
Windows reference (33.4 s).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import sysconfig
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ = ROOT / "requirements-harmonyos.txt"
COMMUNITY_INDEX = "https://pypi.cnb.cool/OpenHarmonyPCDeveloper/pypi/-/packages/simple"
EXPECTED_PLATFORM = "ohos-aarch64"


def run(cmd: list, *, env: dict, dry_run: bool) -> None:
    printable = [str(part) for part in cmd]
    print("+", " ".join(printable), flush=True)
    if dry_run:
        return
    subprocess.run(printable, check=True, text=True, cwd=ROOT, env=env)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install HarmonyOS dependencies.")
    parser.add_argument("--requirements", type=Path, default=REQ)
    parser.add_argument("--index-url", default=COMMUNITY_INDEX)
    parser.add_argument("--skip-raytracepy", action="store_true")
    parser.add_argument("--allow-other-platform", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    platform_tag = sysconfig.get_platform()
    if platform_tag != EXPECTED_PLATFORM and not args.allow_other_platform:
        raise SystemExit(
            f"this interpreter reports platform {platform_tag!r}, expected "
            f"{EXPECTED_PLATFORM!r}.\n"
            "Install the official HarmonyOS runtime first, e.g.\n"
            "  curl -fsSL https://gitcode.com/OpenHarmonyPCDeveloper/cmd-pkgs/"
            "releases/download/pkgs/install-python.sh | sh -s -- 3.12.9\n"
            "and create the venv with ~/usr/local/bin/python3.\n"
            "Pass --allow-other-platform to override."
        )
    if not args.requirements.is_file():
        raise SystemExit(f"missing {args.requirements}")

    env = dict(os.environ)
    env["PIP_INDEX_URL"] = args.index_url

    pip = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--prefer-binary",
        "--index-url",
        args.index_url,
    ]
    if args.dry_run:
        pip.append("--dry-run")

    print(f"== dependencies ({platform_tag}) ==", flush=True)
    run(pip + ["-r", str(args.requirements)], env=env, dry_run=args.dry_run)

    if not args.skip_raytracepy:
        print("== raytracepy (editable) ==", flush=True)
        run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--prefer-binary",
                "--index-url",
                args.index_url,
                "-e",
                str(ROOT),
            ],
            env=env,
            dry_run=args.dry_run,
        )

    print(flush=True)
    print("DONE. Verify with:", flush=True)
    print(f"  {sys.executable} scripts/check_environment.py", flush=True)
    print(f"  {sys.executable} -m pytest -q tests/ -o addopts=''", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
