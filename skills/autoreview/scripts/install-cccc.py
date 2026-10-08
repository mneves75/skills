#!/usr/bin/env python3
"""Install reviewed cccc release bytes at an explicit new path. Python 3.10+, stdlib.

No PATH edits, sudo, replacement or archive-wide extraction. Pins are in
cccc-release.json. Verify the upstream release assets before changing them.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tarfile
import tempfile
import urllib.request


MAX_ARCHIVE = 32 * 1024 * 1024
MAX_BINARY = 64 * 1024 * 1024


def release() -> dict:
    return json.loads(Path(__file__).with_name("cccc-release.json").read_text())


def target(system: str, machine: str) -> str:
    architectures = {"arm64": "aarch64", "aarch64": "aarch64", "x86_64": "x86_64"}
    operating_systems = {"Darwin": "apple-darwin", "Linux": "unknown-linux-musl"}
    if system not in operating_systems or machine not in architectures:
        raise ValueError(f"Unsupported platform: {system}/{machine}; use upstream installation docs")
    return f"{architectures[machine]}-{operating_systems[system]}"


def download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={
        "User-Agent": "OpenAI File Downloader, XaiImageApiFetch/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        if not response.geturl().startswith("https://"):
            raise ValueError("Download redirected outside HTTPS")
        data = response.read(MAX_ARCHIVE + 1)
    if len(data) > MAX_ARCHIVE:
        raise ValueError("Archive exceeds download size limit")
    return data


def install(destination: Path, pin: dict, system: str, machine: str) -> None:
    triple = target(system, machine)
    # lexists also detects dangling symlinks. The final hard link is exclusive,
    # so another installer winning after this preflight cannot be overwritten.
    if os.path.lexists(destination):
        raise FileExistsError(f"Refusing to replace {destination}")
    if not destination.parent.is_dir():
        raise FileNotFoundError(f"Destination directory must already exist: {destination.parent}")
    asset = f"cccc-v{pin['version']}-{triple}.tar.gz"
    url = f"https://github.com/moznion/cccc/releases/download/v{pin['version']}/{asset}"
    data = download(url)
    if hashlib.sha256(data).hexdigest() != pin["sha256"][triple]:
        raise ValueError("SHA-256 mismatch; no binary installed")
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as package:
        members = package.getmembers()
        binaries = [member for member in members if member.name == "cccc"]
        if len(binaries) != 1 or not binaries[0].isreg() or not 0 < binaries[0].size <= MAX_BINARY:
            raise ValueError("Archive must contain exactly one bounded regular cccc binary")
        content = package.extractfile(binaries[0])
        if content is None:
            raise ValueError("Archive binary is unreadable")
        with tempfile.TemporaryDirectory(prefix=".cccc-install-", dir=destination.parent) as temporary:
            staged = Path(temporary) / "cccc"
            with staged.open("xb") as output:
                output.write(content.read(MAX_BINARY + 1))
            staged.chmod(0o755)
            result = subprocess.run([str(staged.resolve()), "--version"], check=True,
                                    capture_output=True, text=True, timeout=15)
            if result.stdout.strip() != f"cccc {pin['version']}":
                raise ValueError("Unexpected cccc version; no binary installed")
            os.link(staged, destination)
    print(f"Installed cccc {pin['version']}: {destination} ({triple}, SHA-256 verified)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="new binary path in an existing directory")
    args = parser.parse_args()
    try:
        install(args.destination.absolute(), release(), platform.system(), platform.machine())
    except (OSError, ValueError, KeyError, tarfile.TarError, subprocess.SubprocessError) as error:
        print(f"cccc installation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
