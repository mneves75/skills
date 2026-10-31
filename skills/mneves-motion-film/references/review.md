# Review round and muted test

Both run in a fresh context on the reviewer seat (a model other than the one that built the
film), from a folder holding only their inputs. Copy the inputs there; never point a reviewer at
the repository.

## Dispatch

- Codex: `codex exec --skip-git-repo-check -s workspace-write -C <dir> -o <dir>/last-message.md - < <dir>/brief.md`.
  The scratch folder is not a Git repository, and Codex refuses to start there without
  `--skip-git-repo-check`, before doing any work: check the run log for that line before
  waiting on it. The muted test runs read-only (`-s read-only`) and attaches the sheets with `-i`.
- Claude: a fresh subagent with only the brief and the folder path.
- Fill `<seconds>`, `<size>`, `<fps>`, `<audience>`, `<platform>` and `<promise>` from the brief.

## Review brief (one new reviewer per round)

```text
Unattended review. You are the reviewer of a <seconds>-second product film. Nobody can answer questions.

Inputs, and the only files you may open:
- ./film.mp4 — the film (<size>, <fps> fps, AAC audio).
- ./facts.json — the only allowed source of on-screen text: an array of {id, text, link}. Every line shown on screen must be a verbatim substring of one fact's text.
Do not open, list or search any other file or directory, and do not use the network. Do not spawn agents.

Audience and intent: <audience> on <platform> (<platform rules: autoplay muted, frame 0 is the thumbnail, bottom 8% covered>). The viewer should end knowing <promise> (product name + URL on the last frame).

Method (do all of it):
1. With ffmpeg, pull one frame every 0.2 s and tile them 20 to a sheet (5x4) with timecodes burned in; look at every sheet. Extract full-size frames wherever you need to read text (at least frame 0, the last frame, and any frame where you suspect a problem).
2. Read every on-screen line and confirm it appears verbatim in facts.json. Report any line that does not, with its timecode.
3. Judge against these rules and report each violation with timecode and severity:
   - Frame 0 is a finished picture with the product name or the point visible.
   - Nothing important in the bottom 8%; text inside safe margins; no overlaps or clipped text.
   - It makes sense muted.
   - Each word held at least 0.3 s and each line at least 0.7 s; text eases in at reading speed and exits quickly.
   - Every keystroke shown causes a visible change on screen.
   - No particles, decorative gradients or glitch effects; no flat screenshots.
   - No frame completely still for more than 0.5 s (ffmpeg freezedetect n=0.001:d=0.5).
   - Close-ups, wide shots and full-screen type alternate; no layout reused in back-to-back scenes.
   - At most six colours; text contrast plausibly 4.5:1 or more.
   - Ends on the product name and URL.
   - Audio: ebur128 integrated about -14 LUFS, true peak at most -1 dBTP; hard cuts land on sound accents.
   <Round 2+: Earlier problems, each to recheck and mark fixed or not: ...>
4. Output, in this order:
   - A numbered problem list, most severe first: [severity: blocker/major/minor] timecode — problem — evidence.
   - "What a muted viewer learns" (3-6 bullets, from the pictures only).
   - The final line, exactly one of: `ship` or `another pass`. Say `ship` only when no blocker or major problem remains.

Write your report to ./report.md as well as returning it.
```

## Muted test brief

Make the sheets with `contact.py film.mp4 sheet --every 0.5 --per-sheet 24`.

```text
Unattended. You are shown contact sheets of a short silent film: frames taken every 0.5 s, in reading order (left to right, top to bottom), each stamped with its timecode. You have no other information about the film, and you must not open any file or use the network.

Retell the story as a viewer who watched it muted:
1. In 4-8 numbered beats, what happens and what you understand at each point (with timecodes).
2. What is the product, what does it do, and why would someone use it?
3. What exactly should the viewer do at the end?
4. Anything that confused you or that you could not read.
Be literal: report only what the pictures show.
```

Compare the retelling with the storyboard's "what the viewer learns" column, beat by beat. A
beat the viewer missed is a picture problem; fix the picture, never the question.
