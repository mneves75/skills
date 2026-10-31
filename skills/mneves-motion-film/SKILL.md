---
name: mneves-motion-film
description: "Make a short product film (demo, launch or explainer video) from a brief, with on-screen text quoted from the product's own pages, music synthesized on a beat grid and a Remotion render, checked for facts, contrast, loudness, codecs and audio sync and reviewed until a fresh reviewer says ship. Use when asked to make, update or redo a product video."
license: Apache-2.0
compatibility: "Python 3.10+ (standard library only), ffmpeg and ffprobe, Node with a Remotion 4 project; capture.py needs Chrome."
---

# Motion film

Turn a brief into a delivered film and the evidence that it is right. Every line on screen is
quoted from the product's own pages, every cut and key press has its sound on the same frame,
and a reviewer who sees only the film and the facts says `ship`. The scripts here do the
measuring; you make the picture.

## Inputs

The brief: product, URL, audience and what they should do at the end. Every other field
(length, format, platform, brand, music, voice, reference video) is yours to decide when the
user leaves it blank. Decide it, then log the choice and the reason in `brief.txt`
([assets/brief.template.txt](assets/brief.template.txt)). Ask only when two readings of the
brief would make different films.

## Layout

In the Remotion project (reuse one the repository already audits; otherwise create one):

```text
film/            brief.txt, facts.json, copy.json, timing.json, theme.json, ledger.txt, capture/
film/scripts/    a copy of this skill's scripts/
src/film/        theme.ts, one component per scene
```

Copy [assets/remotion/](assets/remotion/) to start `src/`, the `*.example.json` files to
start `film/`, and add [assets/eslint.film.mjs](assets/eslint.film.mjs) to the ESLint config.

## Steps

1. **Capture.** `capture.py <url> film/capture` for brand and hierarchy references; copy the
   logo file path for path. Take colours from the product's own styles into `theme.json` (six
   at most). Done when `check_contrast.py film/theme.json` passes.
2. **Facts.** `facts.py <site-url> <page.html>... > film/facts.json`, from the pages as
   served. Ids are text digests, so editing one page line breaks only the copy that quotes it.
   Done when every claim you intend to show is a fact.
3. **Storyboard.** A planner in a fresh context drafts three directions
   ([references/storyboard.md](references/storyboard.md), which also holds the picture and
   sound rules). Choose one and log the strongest rejected alternative. Done when the shot
   table names every shot, line (as fact id), key press and what the viewer learns.
4. **Timing and copy.** Put scenes, cues and the music sections in `timing.json`: every scene
   starts on a beat and carries a `swish` cue on that frame; clicks and hits sit on eighth
   notes. Put each on-screen line in `copy.json` as `{text, fact}`. Done when
   `check_facts.py` passes once the scenes exist.
5. **Build the scenes.** One component per scene, every string through `line()`, every
   timing from `timing.json`. Rebuild the product's screens as live UI with its real text.
   Look at stills (`npx remotion still`) at frame 0, at every key press and at the last frame
   before the first full render.
6. **Build and check.** `python3 -B film/scripts/build.py --composition <id>` runs, in order:
   facts trace, contrast, music, loudness (mix and music alone), render, mux, muted copy,
   media checks, sync, contact sheets. Done when it exits 0. Read every contact sheet
   yourself: overflow, clipped text, a still hold, a key press with no visible change.
7. **Review rounds.** Each round, a new reviewer on the reviewer seat (never the model that
   built it) sees only `film.mp4` and `facts.json`; the same round, a muted test retells the
   film from 2 fps sheets ([references/review.md](references/review.md) holds both briefs and
   the dispatch). Fix the worst problem first, rebuild, and give the next reviewer the earlier
   problems to recheck. Done when a reviewer's last line is `ship`, at most five rounds; after
   five, deliver with the open problems listed.
8. **Ledger.** Record every round in `ledger.txt`
   ([assets/ledger.template.txt](assets/ledger.template.txt)): the numbers the scripts printed,
   before and after each fix, and the reviewer's verdict. A number nobody measured stays out.

## Scripts

Standard library and ffmpeg only; each prints its usage when run without arguments and exits 1
on a failed check.

| Script | Checks or makes |
|---|---|
| `capture.py` | headless Chrome stills: hero, full page, phone |
| `facts.py` | facts.json from the product's pages |
| `check_facts.py` | every copy line a verbatim substring of its fact; every line shown; no unknown `line()` id |
| `check_contrast.py` | at most six colours; every text pair at least 4.5:1 |
| `music.py` | music and effects from timing.json, fixed seed |
| `loudness.py` | two-pass loudnorm to -14 LUFS, true peak at most -1 dBTP, measured after |
| `check_media.py` | size, frame rate, duration, H.264 yuv420p, AAC 48 kHz, faststart |
| `check_sync.py` | cuts on the beat with a swish; every kick, click, hit and final chord within one frame |
| `contact.py` | timecoded contact sheets |
| `build.py` | all of the above in order, stopping at the first failure |

`tests/test_pipeline.py` proves each check passes on a good film and refuses its own planted
violation.

## Deliver

`film.mp4`, the music alone (`music.wav`), the 15-frame thumbnail sheet, `brief.txt`,
`facts.json`, `timing.json` and `ledger.txt`. Name the seconds the user should watch and listen
to themselves: the first second (the thumbnail), each key press, the loudest section and the
end card. A site that embeds the film also gets its poster from frame 0 and captions that
describe the sound.

## Gotchas

- Remotion's headless Chrome does not resolve `-apple-system`; put `system-ui` first.
- Render with `--image-format=png`: JPEG frames come out yuvj420p, which some players reject.
- Six colours means six solid colours on screen: borders take a palette colour rather than ink
  at low opacity, panels take no grey fill, nothing is dimmed for long, and a logo's near-white
  is drawn in the palette's ink.
- Phone players shrink a 1920 px frame about five times: terminal type under about 70 px
  becomes unreadable. Show a prefix of each line (still a substring of its fact) in a close-up
  rather than the whole line small.
- When the product's real screen differs from what the film needs to show (a row left out, a
  state after a key), capture that real screen into the product's pages first, so it becomes a
  fact; never compose a line from permitted pieces.
- Put key presses on a kick or a quiet eighth: a click on an open hat is masked by its noise,
  and `check_sync.py` cannot measure it.
- Codex refuses to start outside a Git repository without `--skip-git-repo-check`; a review
  that exits at once has not reviewed anything.
