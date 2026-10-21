# SM-2 Spaced Repetition Algorithm

Reference for the SuperMemo 2 algorithm used by the SRS database.

## Core Formula

After each review with quality rating `q` (0-5):

### Ease Factor Update
```
EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
EF' = max(1.3, EF')
```

### Interval Calculation

**If quality >= 3 (successful recall):**
- 1st successful review: interval = 1 day
- 2nd successful review: interval = 6 days
- Subsequent: interval = round(previous_interval * EF)

**If quality < 3 (failed recall):**
- Reset repetitions to 0
- Interval = 1 day (start over)

## Quality Scale Semantics

| Score | Label | Behavioral Signal |
|-------|-------|-------------------|
| 0 | Blackout | No memory at all |
| 1 | Wrong + vague | Faint recognition when shown answer |
| 2 | Wrong + familiar | Recognized answer but couldn't produce it |
| 3 | Correct + hard | Significant effort to recall |
| 4 | Correct + hesitation | Some thinking required |
| 5 | Perfect | Immediate, confident recall |

## Ease Factor Interpretation

| EF Range | Meaning | Action |
|----------|---------|--------|
| >= 2.5 | Easy material | Card is well-learned |
| 2.0 - 2.5 | Normal | Standard progression |
| 1.5 - 2.0 | Difficult | Consider breaking card into simpler pieces |
| 1.3 (floor) | Very hard | Card may need rewriting or additional context |

## Mastery Definition

A card is considered "mastered" when:
- `repetitions >= 5` AND `ease_factor >= 2.5`

A card is "struggling" when:
- `ease_factor < 1.8`

## Interval Progression Examples

Starting from EF=2.5, perfect recalls (q=5). The helper updates EF first, then multiplies the
previous interval by the new EF:
```
Review 1: 1 day    (EF = 2.5 + 0.1 = 2.6)
Review 2: 6 days   (EF = 2.7)
Review 3: 17 days  (6 * 2.8 = 16.8 → 17)
Review 4: 49 days  (17 * 2.9 = 49.3 → 49)
Review 5: 147 days (49 * 3.0 = 147)
```

With mediocre recalls (q=3), each review changes EF by 0.1 - 2 * (0.08 + 2 * 0.02) = -0.14:
```
Review 1: 1 day   (EF = 2.36)
Review 2: 6 days  (EF = 2.22)
Review 3: 12 days (6 * 2.08 = 12.48 → 12)
Review 4: 23 days (12 * 1.94 = 23.28 → 23)
```

Notice how quality=3 barely passes but steadily decreases EF, making reviews more frequent; the algorithm adapts to difficulty.
