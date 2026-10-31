#!/usr/bin/env python3
"""End-to-end controls for the film scripts, without Remotion or a network.

usage: python3 tests/test_pipeline.py

Synthesizes the music for a 4 s timing, normalises it, muxes it under a
synthetic ffmpeg picture and requires every check to pass; then plants one
violation per check (audio two frames late, yuv444p, a misquoted line, a line
never shown, a low-contrast pair, a seventh colour, a cut off the beat) and
requires each to fail. Needs python3 and ffmpeg/ffprobe on PATH.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
PY = [sys.executable, "-B"]

TIMING = {
    "fps": 60, "bpm": 120, "beatFrames": 30, "durationFrames": 240, "width": 320, "height": 180,
    "scenes": [{"id": "a", "from": 0, "to": 120}, {"id": "b", "from": 120, "to": 240}],
    "cues": [{"frame": 120, "kind": "swish", "scene": "b"}, {"frame": 150, "kind": "click", "key": "x"}],
    "music": {
        "chords": [[57, 60, 64], [53, 57, 60]],
        "sections": [{"from": 0, "to": 6, "voices": ["pad", "kick", "hat", "bass", "arp"]}],
        "final": {"beat": 6, "chord": [57, 60, 64, 69]},
    },
}
THEME = {
    "colours": {"bg": "#0a0a0a", "ink": "#efefec", "accent": "#c8ff38"},
    "text": {"body": ["ink", "bg"], "accent": ["accent", "bg"]},
}
FACTS = [{"id": "f00000001", "text": "Preview first. Approve once.", "link": "https://example.test/"}]
COPY = {"head": {"text": "Approve once.", "fact": "f00000001"}}
SOURCE = 'export const Head = () => <h1>{line("head")}</h1>;\n'

failures: list[str] = []


def run(name: str, args: list[str], expect_ok: bool) -> None:
    result = subprocess.run(args, capture_output=True, text=True, timeout=600)
    ok = result.returncode == 0
    if ok == expect_ok:
        # The check's own last word, so a refusal can be seen to refuse for the planted reason.
        lines = (result.stdout + result.stderr).strip().splitlines()
        said = next((line for line in lines if line.startswith("FAIL")), lines[-1] if lines else "")
        print(f"PASS {name}: exit {result.returncode}: {said[:150]}")
    else:
        failures.append(name)
        print(f"FAIL {name}: exit {result.returncode}, expected {'0' if expect_ok else 'nonzero'}")
        print(result.stdout[-1500:], result.stderr[-1500:], sep="\n")


def write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def ffmpeg(*args: str) -> None:
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True, timeout=300)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="motion-film-test-") as tmp:
        root = Path(tmp)
        timing = write_json(root / "timing.json", TIMING)
        size = ["--width", "320", "--height", "180", "--fps", "60", "--seconds", "4"]

        run("music", PY + [str(SCRIPTS / "music.py"), str(timing), str(root)], True)
        run("loudness", PY + [str(SCRIPTS / "loudness.py"), str(root / "mix.wav"), str(root / "mix-norm.wav")], True)
        ffmpeg("-f", "lavfi", "-i", "testsrc2=size=320x180:rate=60:duration=4", "-pix_fmt", "yuv420p", "-c:v", "libx264", str(root / "picture.mp4"))
        mux = ["-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-ar", "48000", "-movflags", "+faststart", "-shortest"]
        ffmpeg("-i", str(root / "picture.mp4"), "-i", str(root / "mix-norm.wav"), *mux, str(root / "film.mp4"))
        run("media", PY + [str(SCRIPTS / "check_media.py"), str(root / "film.mp4"), *size, "--audio"], True)
        run("sync", PY + [str(SCRIPTS / "check_sync.py"), str(timing), str(root / "film.mp4")], True)
        run("contact sheet", PY + [str(SCRIPTS / "contact.py"), str(root / "film.mp4"), str(root / "contact"), "--every", "0.5"], True)

        # Planted violations: each check must refuse its own failure.
        ffmpeg("-i", str(root / "mix-norm.wav"), "-af", "adelay=33:all=1", str(root / "late.wav"))
        ffmpeg("-i", str(root / "picture.mp4"), "-i", str(root / "late.wav"), *mux, str(root / "late.mp4"))
        run("sync refuses audio two frames (33 ms) late", PY + [str(SCRIPTS / "check_sync.py"), str(timing), str(root / "late.mp4")], False)
        off_grid = json.loads(json.dumps(TIMING))
        off_grid["scenes"][1]["from"] = 121
        run("sync refuses a cut off the beat", PY + [str(SCRIPTS / "check_sync.py"), str(write_json(root / "off.json", off_grid)), str(root / "film.mp4")], False)
        ffmpeg("-f", "lavfi", "-i", "testsrc2=size=320x180:rate=60:duration=4", "-pix_fmt", "yuv444p", "-c:v", "libx264", "-movflags", "+faststart", str(root / "444.mp4"))
        run("media refuses yuv444p", PY + [str(SCRIPTS / "check_media.py"), str(root / "444.mp4"), *size], False)

        facts = write_json(root / "facts.json", FACTS)
        src = root / "src"
        src.mkdir()
        (src / "Head.tsx").write_text(SOURCE, encoding="utf-8")
        run("facts", PY + [str(SCRIPTS / "check_facts.py"), str(facts), str(write_json(root / "copy.json", COPY)), str(src)], True)
        misquoted = {"head": {"text": "Approve twice.", "fact": "f00000001"}}
        run("facts refuse a misquote", PY + [str(SCRIPTS / "check_facts.py"), str(facts), str(write_json(root / "bad.json", misquoted)), str(src)], False)
        unshown = {**COPY, "tail": {"text": "Preview first.", "fact": "f00000001"}}
        run("facts refuse a line never shown", PY + [str(SCRIPTS / "check_facts.py"), str(facts), str(write_json(root / "unshown.json", unshown)), str(src)], False)

        run("contrast", PY + [str(SCRIPTS / "check_contrast.py"), str(write_json(root / "theme.json", THEME))], True)
        low = json.loads(json.dumps(THEME))
        low["colours"]["grey"] = "#444444"
        low["text"]["faint"] = ["grey", "bg"]
        run("contrast refuses a faint pair", PY + [str(SCRIPTS / "check_contrast.py"), str(write_json(root / "low.json", low))], False)
        many = json.loads(json.dumps(THEME))
        many["colours"].update({f"c{i}": "#ffffff" for i in range(4)})
        run("contrast refuses a seventh colour", PY + [str(SCRIPTS / "check_contrast.py"), str(write_json(root / "many.json", many))], False)

    print(f"test_pipeline.py: {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
