#!/usr/bin/env python3
"""Install requirements-harmonyos.txt (+ editable raytracepy). Does not modify source.

    python scripts/install_dependencies_harmonyos.py
    python scripts/install_dependencies_harmonyos.py --dry-run
    python scripts/install_dependencies_harmonyos.py --skip-raytracepy
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ = ROOT / "requirements-harmonyos.txt"
HNP_BIN = Path("/data/service/hnp/bin")


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, text=True, cwd=ROOT)


def main() -> int:
    p = argparse.ArgumentParser(description="Install HarmonyOS dependency pins.")
    p.add_argument("--requirements", type=Path, default=REQ)
    p.add_argument("--skip-raytracepy", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if sys.version_info < (3, 10):
        raise SystemExit(f"need Python >= 3.10, got {sys.version}")
    if not args.requirements.is_file():
        raise SystemExit(f"missing {args.requirements}")

    if HNP_BIN.is_dir():
        path = os.environ.get("PATH", "")
        hnp = str(HNP_BIN)
        if hnp not in path.split(os.pathsep):
            os.environ["PATH"] = hnp + os.pathsep + path

    print("NOTE: numba JIT SIGSEGV on HarmonyOS — use task-5 njit fallback.", flush=True)

    pip = [sys.executable, "-m", "pip", "install"]
    if args.dry_run:
        pip.append("--dry-run")
    run(pip + ["-r", str(args.requirements)])
    if not args.skip_raytracepy:
        run(pip + ["-e", str(ROOT)])

    print("DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
