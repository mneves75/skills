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
import os
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
        run("sync", PY + [str(SCRIPTS / "check_sync.py"), str(timing), str(root / "film.mp4"), "--sfx", str(root)], True)
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
        # The click sits on a kick: the mix alone would pass without it, its own stem does not.
        silent = root / "no-click"
        silent.mkdir()
        no_click = {**TIMING, "cues": [c for c in TIMING["cues"] if c["kind"] != "click"]}
        run("music without the click", PY + [str(SCRIPTS / "music.py"), str(write_json(silent / "timing.json", no_click)), str(silent)], True)
        run("sync refuses a missing click", PY + [str(SCRIPTS / "check_sync.py"), str(timing), str(root / "film.mp4"), "--sfx", str(silent)], False)
        # A kick expected on frame 0 over silence: the strongest of nothing is not an attack.
        only_kick = {"fps": 60, "bpm": 120, "scenes": [{"id": "a", "from": 0, "to": 240}], "cues": [],
                     "music": {"sections": [{"from": 0, "to": 1, "voices": ["kick"]}]}}
        ffmpeg("-i", str(root / "picture.mp4"), "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", *mux, "-t", "4", str(root / "hush.mp4"))
        run("sync refuses a frame-0 kick over silence",
            PY + [str(SCRIPTS / "check_sync.py"), str(write_json(root / "kick0.json", only_kick)), str(root / "hush.mp4")], False)
        # Frame 0 alone is white: the first tile of the sheet, stamped 0 s, must be that frame.
        ffmpeg("-f", "lavfi", "-i", "color=black:size=320x180:rate=60:duration=2",
               "-vf", "drawbox=c=white:t=fill:enable='eq(n,0)'", "-pix_fmt", "yuv420p", "-c:v", "libx264", str(root / "first.mp4"))
        run("contact sheet of the white frame", PY + [str(SCRIPTS / "contact.py"), str(root / "first.mp4"), str(root / "first"), "--every", "0.2"], True)
        tile = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(root / "first-01.png"),
                               "-vf", "crop=100:60:150:100,scale=1:1", "-pix_fmt", "gray", "-f", "rawvideo", "-"],
                              capture_output=True, check=True, timeout=60).stdout
        if tile and tile[0] > 200:
            print(f"PASS contact sheet's 0 s tile is frame 0 (luma {tile[0]})")
        else:
            failures.append("contact sheet's 0 s tile is frame 0")
            print(f"FAIL contact sheet's 0 s tile is frame 0 (luma {tile[0] if tile else None})")
        # Every other frame dropped after 2 s: the timestamp base still says 60.
        ffmpeg("-i", str(root / "film.mp4"), "-vf", "select=lt(t\\,2)+not(mod(n\\,2))", "-fps_mode", "vfr", "-c:v", "libx264",
               "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", str(root / "vfr.mp4"))
        run("media refuses a variable frame rate", PY + [str(SCRIPTS / "check_media.py"), str(root / "vfr.mp4"), *size, "--audio"], False)

        facts = write_json(root / "facts.json", FACTS)
        src = root / "src"
        src.mkdir()
        (src / "Head.tsx").write_text(SOURCE, encoding="utf-8")
        run("facts", PY + [str(SCRIPTS / "check_facts.py"), str(facts), str(write_json(root / "copy.json", COPY)), str(src)], True)
        misquoted = {"head": {"text": "Approve twice.", "fact": "f00000001"}}
        run("facts refuse a misquote", PY + [str(SCRIPTS / "check_facts.py"), str(facts), str(write_json(root / "bad.json", misquoted)), str(src)], False)
        unshown = {**COPY, "tail": {"text": "Preview first.", "fact": "f00000001"}}
        run("facts refuse a line never shown", PY + [str(SCRIPTS / "check_facts.py"), str(facts), str(write_json(root / "unshown.json", unshown)), str(src)], False)
        single = root / "src-single"
        single.mkdir()
        (single / "Head.tsx").write_text(SOURCE.replace('"head"', "'head'"), encoding="utf-8")
        run("facts accept a single-quoted line()", PY + [str(SCRIPTS / "check_facts.py"), str(facts), str(root / "copy.json"), str(single)], True)
        (single / "Tail.tsx").write_text("export const Tail = () => <p>{line('tail')}</p>;\n", encoding="utf-8")
        run("facts refuse a single-quoted unknown id", PY + [str(SCRIPTS / "check_facts.py"), str(facts), str(root / "copy.json"), str(single)], False)
        page = root / "index.html"
        page.write_text("<!doctype html><title>t</title><p>Preview first. Approve once.</p>\n", encoding="utf-8")
        made = subprocess.run(PY + [str(SCRIPTS / "facts.py"), "https://example.test/", str(page)], capture_output=True, text=True, check=True)
        (root / "made.json").write_text(made.stdout, encoding="utf-8")
        check = PY + [str(SCRIPTS / "facts.py"), "--check", str(root / "made.json"), "https://example.test/", str(page)]
        run("facts match their page", check, True)
        page.write_text("<!doctype html><title>t</title><p>Preview first. Approve twice.</p>\n", encoding="utf-8")
        run("facts refuse a page edited since", check, False)

        run("contrast", PY + [str(SCRIPTS / "check_contrast.py"), str(write_json(root / "theme.json", THEME))], True)
        low = json.loads(json.dumps(THEME))
        low["colours"]["grey"] = "#444444"
        low["text"]["faint"] = ["grey", "bg"]
        run("contrast refuses a faint pair", PY + [str(SCRIPTS / "check_contrast.py"), str(write_json(root / "low.json", low))], False)
        many = json.loads(json.dumps(THEME))
        many["colours"].update({f"c{i}": "#ffffff" for i in range(4)})
        run("contrast refuses a seventh colour", PY + [str(SCRIPTS / "check_contrast.py"), str(write_json(root / "many.json", many))], False)

        # build.py runs the project's ESLint (react/jsx-no-literals) before it renders, with a stub
        # npx: a failing lint stops the build there; a passing one lets it go on to the music.
        film = root / "build-film"
        film.mkdir()
        page.write_text("<!doctype html><title>t</title><p>Preview first. Approve once.</p>\n", encoding="utf-8")
        made = subprocess.run(PY + [str(SCRIPTS / "facts.py"), "https://example.test/", str(page)], capture_output=True, text=True, check=True)
        (film / "facts.json").write_text(made.stdout, encoding="utf-8")
        fact_id = next(f["id"] for f in json.loads(made.stdout) if "Approve once." in f["text"])
        write_json(film / "copy.json", {"head": {"text": "Approve once.", "fact": fact_id}})
        write_json(film / "timing.json", TIMING)
        write_json(film / "theme.json", THEME)
        build = PY + [str(SCRIPTS / "build.py"), "--composition", "Film", "--site", "https://example.test/", "--page", str(page),
                      "--film", str(film), "--src", str(src), "--out", str(root / "build-out")]
        for lint_exit, name in ((1, "build stops at a failing JSX lint"), (0, "build goes past a passing JSX lint")):
            stub = root / f"bin-{lint_exit}"
            stub.mkdir()
            (stub / "npx").write_text(f'#!/bin/sh\n[ "$1" = eslint ] && exit {lint_exit}\nexit 0\n', encoding="utf-8")
            (stub / "npx").chmod(0o755)
            env = {**os.environ, "PATH": f"{stub}:{os.environ['PATH']}"}
            result = subprocess.run(build, capture_output=True, text=True, timeout=600, env=env)
            said = result.stdout + result.stderr
            stopped = "jsx literals failed" in said
            went_on = "==> music" in said
            ok = (stopped and not went_on) if lint_exit else (went_on and not stopped)
            print(f"{'PASS' if ok else 'FAIL'} {name}: exit {result.returncode}")
            if not ok:
                failures.append(name)
                print(said[-1500:])

    print(f"test_pipeline.py: {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
