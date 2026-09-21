"""Build a self-contained Headroom runtime bundle for Pulse.

Run this from a clean checkout at the revision being released. The output is a
zip plus a manifest entry that Pulse can pin by revision, size, and SHA-256.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "pulse"


def normalized_platform() -> str:
    return {"Darwin": "darwin", "Linux": "linux", "Windows": "win32"}[platform.system()]


def normalized_arch() -> str:
    machine = platform.machine().lower()
    return "arm64" if machine in {"aarch64", "arm64"} else "x64"


def main() -> None:
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    target = f"headroom-pulse-{revision[:12]}-{normalized_platform()}-{normalized_arch()}"
    work = DIST / "work"
    shutil.rmtree(work, ignore_errors=True)
    DIST.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "pyinstaller",
            "--noconfirm",
            "--clean",
            "--onedir",
            "--name",
            "headroom",
            "--distpath",
            str(work / "dist"),
            "--workpath",
            str(work / "build"),
            "--specpath",
            str(work),
            "--collect-all",
            "headroom",
            "--collect-all",
            "litellm",
            str(ROOT / "packaging" / "pulse_headroom_entry.py"),
        ],
        cwd=ROOT,
        check=True,
    )

    executable = "headroom.exe" if os.name == "nt" else "headroom"
    subprocess.run([str(work / "dist" / "headroom" / executable), "--version"], check=True)
    archive = shutil.make_archive(
        str(DIST / target), "zip", root_dir=work / "dist", base_dir="headroom"
    )
    archive_path = Path(archive)
    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    manifest = {
        "schemaVersion": 1,
        "revision": revision,
        "platform": normalized_platform(),
        "architecture": normalized_arch(),
        "archive": archive_path.name,
        "archiveBytes": archive_path.stat().st_size,
        "sha256": digest,
        "executable": f"headroom/{executable}",
    }
    (DIST / f"{target}.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
