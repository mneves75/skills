# Storyboard brief and picture rules

## Storyboard brief (planner seat, fresh context)

Give it brief.txt, facts.json and the capture stills. Ask for:

```text
Three different directions for a <seconds>-second film for <audience> on <platform>. For each:
- a one-line idea and why this audience would watch to the end;
- a shot table: start time (on the beat grid of <bpm> BPM), shot type (wide / close-up /
  full-screen type), what is on screen, the exact on-screen lines as fact ids from facts.json,
  every keystroke and the visible change it causes, and "what the viewer learns" in this shot;
- the music arc (where it builds, drops and resolves) and every sound effect, each tied to an
  on-screen event;
- the strongest objection to this direction.
Then recommend one and say what the other two would do better.
Only facts.json text may appear on screen, verbatim. No voice-over.
```

Pick one, log the choice and the strongest rejected alternative in brief.txt, and keep the
shot table as the plan: every later change goes back into timing.json and copy.json.

## Picture rules

- Frame 0 is the thumbnail: a finished picture with the name or the point, never a fade-in.
- Keep the bottom 8% clear of anything important (mobile players cover it); safe margins on
  every side.
- It must make sense muted: every step is written or shown, never only heard.
- Each word holds at least 0.3 s and each line at least 0.7 s. Text eases in at reading speed
  and leaves fast; every move is eased at both ends.
- Every keystroke shown causes a visible change, on the frame its click sounds.
- No flat screenshots: rebuild the product's screens as live UI with the real text. No
  particles, decorative gradients or glitch effects.
- No frame is still for more than 0.5 s: holds keep a slow push or drift.
- Alternate wide shots, close-ups and full-screen type; never reuse a layout in back-to-back
  scenes.
- Six colours at most, taken from the product's own styles; every text pair at least 4.5:1.
- End on the product name and URL, held long enough to read.

## Sound rules

- Music synthesized in code on a beat grid; hard cuts land on beats.
- Sound effects only for on-screen events: a swish on a cut, a click on a key press, a hit on a
  result.
- Delivery loudness about -14 LUFS integrated, true peak at most -1 dBTP; also deliver the
  music alone at the same loudness.
