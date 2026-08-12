---
name: fztbucs-design
description: Use this skill to generate well-branded interfaces and assets for fztbucs — a web product with Editorial Tech Minimalism aesthetics. Contains essential design guidelines, colors, type, fonts, and UI kit components for prototyping web UIs.
user-invocable: true
---

# fztbucs Design Skill

Read the `README.md` file within this skill, and explore the other available files.

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out
and create static HTML files for the user to view. If working on production code, you can
copy assets and read the rules here to become an expert in designing with this brand.

If the user invokes this skill without any other guidance, ask them what they want to build
or design, ask some questions, and act as an expert designer who outputs HTML artifacts
_or_ production code, depending on the need.

## Quick map

- `README.md` — brand context, content fundamentals, visual foundations (read first)
- `css.json` — structured token understanding source
- `colors_and_type.css` — drop-in runtime CSS variables; link it, do not read it to understand tokens when css.json exists
- `components/_evidence/` — compact component specifications for evidence-backed Figma libraries
- resolved component sources — create-library uses `preview/component-{slug}.html` first, `components/{slug}.json` for intent/variants, and `components/_evidence/{slug}.json` as fallback evidence
- `preview/` — small HTML cards illustrating the foundations and components
- `ui_kits/{type}/` — full click-thru recreation (use as reference for layout, density, patterns)
- `library-consumption.json` — recommended downstream read order

## Essentials at a glance

- **Brand primary is mode-aware:** light mode uses deep navy `#1e40af`; dark mode flips to amber gold `#d4a574`. The background is a distinctive light pinkish `#fdf5f7` in light mode and pure `#000000` in dark mode.
- **Editorial squared corners are the default:** controls and cards use `0px` radius; the only soft shapes are capsules at `28px` and capsule items at `22px`. Rounded buttons or cards are off-brand.
- **Type is triplex:** display/headings use **Fraunces** (with `Noto Serif SC` fallback), metadata and labels use **JetBrains Mono** uppercase, body copy uses **Noto Sans SC**. Never default to a generic system sans.
- **Buttons are uppercase mono pills-within-a-square:** `12px` uppercase JetBrains Mono, `0.1em` letter-spacing, `0.75rem 1.5rem` padding, squared edges; hover is `opacity: 0.9`, disabled is `opacity: 0.3`.
- **Shadows are whisper-quiet:** only two layers exist — popover `0 4px 24px rgba(0,0,0,0.04)` and modal `0 8px 40px rgba(0,0,0,0.08)`. No heavy elevation at rest.
- **Spacing and motion are measured:** base radius is `4px` for input fields, motion uses `cubic-bezier(0.16, 1, 0.3, 1)` with a `800ms` cinematic duration for hero reveals.
- **Voice is Chinese-first, technical, and restrained:** prefer exact editorial labels, avoid emoji in product UI, and reserve serif italics for occasional keyword emphasis.
