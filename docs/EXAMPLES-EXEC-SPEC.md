# Engineering Spec: Visual Examples & Professional README

## Problem Statement

The skills repository lacks visual demonstration of capabilities. Users must read documentation and imagine what the tool does rather than seeing it immediately.

**Current state:** Text-only README with no visual proof of value.

**Goal:** Repository that impresses within 5 seconds of landing.

## Success Criteria

1. Hero screenshot visible without scrolling
2. Examples folder with real benchmark outputs
3. Professional badges (version, license, tools)
4. Version consistency (all references show 1.0.0)

## Research Findings

From [awesome-readme](https://github.com/matiassingers/awesome-readme) and [Best-README-Template](https://github.com/othneildrew/Best-README-Template):

> "Elements in beautiful READMEs include: images, screenshots, GIFs, text formatting"
> "Stick to 4-7 badges. Essential: version, license. Optional: downloads, TypeScript support"

Best examples: [httpie/httpie](https://github.com/httpie/httpie), [lobehub/lobe-chat](https://github.com/lobehub/lobe-chat) - lead with visuals.

## Implementation Plan

### Phase 1: Generate Example Reports

1. Run readiness-check against a sample project
2. Generate HTML, JSON, and Markdown outputs
3. Save to `examples/` folder

### Phase 2: Visual Assets

1. Screenshot the HTML dashboard (hero image)
2. Save as `assets/demo-dashboard.png`
3. Create terminal output example image

### Phase 3: README Enhancement

1. Add shields.io badges:
   - Version: `![Version](https://img.shields.io/badge/version-1.0.0-blue)`
   - License: `![License](https://img.shields.io/badge/license-Apache--2.0-green)`
   - Tools: `![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-purple)`

2. Add hero image after title
3. Link to examples folder
4. Update all version references to 1.0.0

### Phase 4: Version Consistency

1. Update SKILL.md version reference
2. Ensure HTML template says v1.0.0

## File Structure

```
skills/
├── assets/
│   └── demo-dashboard.png          # Hero screenshot
├── examples/
│   ├── README.md                   # Examples index
│   └── fastapi.html                # Python project assessment
├── README.md                       # Updated with visuals
└── VERSION                         # 1.0.0
```

## Verification

- [x] Hero image visible on GitHub without scrolling
- [x] Examples folder contains working HTML report
- [x] All badges render correctly
- [x] Version shows 1.0.0 everywhere
- [x] HTML report opens in browser correctly
