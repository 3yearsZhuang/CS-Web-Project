# fztbucs Design System

A design system reconstruction of **fztbucs** — a web product built around Editorial Tech Minimalism.
The system is purpose-built for content-forward web interfaces that need the warmth of editorial typography and the precision of technical tooling.

> *"编辑式技术极简 (Editorial Tech Minimalism) — 浅色模式强调色：深蓝 #1e40af；深色模式强调色：琥珀金 #d4a574"* — source comment in `colors_and_type.css`

## Source

- **Structured spec:** `.design_library/fztbucs/css.json`, `colors_and_type.css`, and `components/*.json`
- **Components:** 6 documented components covering navigation, feedback, data entry, and content surfaces
- **Brand owner:** fztbucs

## What this design system covers

- **Foundations** — color (light/dark), typography (Fraunces / JetBrains Mono / Noto Sans SC), spacing, radius, shadow, and motion
- **Components** — 6 documented components: Button, Input, Card, Navbar, Toast, Avatar
- **Sample slides & UI kit** — reference previews in `preview/` and full click-through UI kits in `ui_kits/` when present

---

## CONTENT FUNDAMENTALS

### Voice & tone

fztbucs speaks in a Chinese-first, editorial-technical register. Copy is precise, unhurried, and visually self-aware: headings and labels feel like they were set by a publication designer rather than a generic SaaS product. The tone is professional and neutral, never chatty, and avoids emoji entirely in product UI. English appears only for functional labels (class names, token slugs, component anatomy) and short uppercase mono tags such as section markers `[01]`, `[02]`. When the interface needs emphasis, it leans on typography — a serif italic keyword or a small uppercase mono label — rather than exclamation marks or warm colloquialisms.

### Concrete copy examples (lifted from the source)

- Design ethos: *"编辑式技术极简 (Editorial Tech Minimalism)"*
- Light mode note: *"浅色模式强调色：深蓝 #1e40af"*
- Dark mode note: *"深色模式强调色：琥珀金 #d4a574"*
- Utility class description: *"运行时字体组合栈"*
- Button system label: *"统一按钮系统 — 编辑式技术极简"*
- Section marker style: *"[01] [02] 风格"* and uppercase mono tags

### When generating copy

- Lead in Chinese; keep English to token names, class names, and short uppercase labels.
- Prefer exact, almost catalog-like descriptions over marketing flourish.
- Use uppercase mono tags (`[01]`, `[02]`) for chapter or section markers.
- Avoid emoji, exclamation-heavy sentences, and generic CTA language.
- Reserve serif italics for one-word emphasis within otherwise sans body copy.

---

## Visual Foundations

### Color

The palette is built on a deliberate contrast between a warm, light-pinkish page and a cool, deep navy accent. In light mode, the page background is `#fdf5f7`, foreground text is the near-black-purple `#1e1233`, and the primary action color is deep navy `#1e40af`. Cards and popovers sit cleanly on white `#ffffff`, while secondary surfaces use `#f0e8ee` and muted backgrounds use `#f8eef2`. The accent slot `#e8ecf5` provides a cool blue-gray for highlights without competing with primary.

Semantic colors are sparse and functional: destructive is a sharp red `#e7000b`; success, warning, and info are drawn from the chart scale rather than introducing extra hues. The chart palette in light mode runs `#1e40af` through `#ec4899`, `#14b8a6`, `#6366f1`, and `#8b5cf6`. Logo colors add a soft gradient vocabulary: `#4070e0`, `#80a0f0`, `#a0d0f0`, `#f0b0c0`, and `#f0c0d0`.

In dark mode, the palette inverts dramatically: background becomes `#000000`, cards become `#0a0a0a`, and foreground warms to `#f5f5f4`. The primary accent switches from navy to amber gold `#d4a574`, and the ring follows the same gold. Chart colors are re-balanced for dark surfaces, shifting to `#d4a574`, `#5bc9c5`, `#e88565`, `#c77dba`, and `#8b9dc3`. The overall vibe is gallery-like in light mode and nocturnal-editorial in dark mode.

### Typography

The type system is explicitly triplex. **Fraunces** (with `Noto Serif SC` as the Chinese fallback) handles display and editorial headings — it is used at a light weight of `350` with optical sizing enabled and a tight line-height around `1.05`. **JetBrains Mono** handles all meta text: uppercase section markers, labels, buttons, error messages, and tags at sizes like `11px` or `12px` with letter-spacing between `0.08em` and `0.15em`. **Noto Sans SC** carries body copy and UI labels, loaded via Google Fonts with weights `300..700`.

Because the CSS imports only Noto Sans SC and Noto Serif SC at runtime, Fraunces and JetBrains Mono are expected to be supplied by the consuming project (commonly through Next.js font optimization). Fallbacks are specified: for Fraunces the chain is `Noto Serif SC`, `Songti SC`, then generic serif; for JetBrains Mono the chain is `SFMono-Regular`, `Menlo`, `Monaco`, `Consolas`, then generic monospace.

### Spacing

Spacing is anchored by a `4px` base. The radius token is `0.25rem` (`4px`), from which a derived scale runs from `radius-sm` (`calc(var(--radius) - 4px)`) through `radius-4xl` (`calc(var(--radius) + 16px)`). Buttons use generous padding (`0.75rem 1.5rem` for medium, `0.375rem 0.75rem` for small), while input fields take compact internal padding and stretch full-width. Z-index layers are also tokenized from `10` up to `9998` for overlays.

### Radius

- **`0px`** — the default for buttons, cards, tags, badges, and toast containers; the editorial squared corner is the brand signature.
- **`4px`** — used for input fields only (`INPUT_CLASS` exception); this is the single place where a rounded corner appears in the control set.
- **`28px`** — reserved for capsule-shaped elements.
- **`22px`** — used for items inside capsules.

The near-total absence of rounding is intentional: it gives the interface the feel of a printed page or a technical document rather than a conventional rounded web app.

### Shadow / Elevation

Only two shadow layers are defined, both extremely restrained:

1. **Popover (level 1):** `0 4px 24px rgba(0, 0, 0, 0.04)` — used for dropdowns, popovers, and small floating panels.
2. **Modal (level 2):** `0 8px 40px rgba(0, 0, 0, 0.08)` — used for dialogs and larger overlays.

Elevation is not used to distinguish cards from the page; cards rely on white (`#ffffff`) background against the pinkish `#fdf5f7` page. The shadow philosophy is "whisper-quiet" — surfaces read as flat until they genuinely need to float.

### Borders, backgrounds, and motion

Borders are hair-thin and low-contrast: `rgba(30, 18, 51, 0.08)` in light mode and `rgba(255, 255, 255, 0.06)` in dark mode. Input borders are slightly stronger at `0.1` opacity. A dedicated `.hairline` utility draws `1px` solid `var(--border)` to separate editorial sections. Motion uses a custom easing `cubic-bezier(0.16, 1, 0.3, 1)` (`--ease-ark`) with durations ranging from `200ms` for fast feedback to `800ms` for cinematic hero reveals and `1400ms` for epic transitions.

---

## Component Patterns

| Component | Preview | Contract | CSS Source | Key Facts | Key Insight |
|---|---|---|---|---|---|
| Button | `preview/component-button.html` | `components/button.json` | `colors_and_type.css` (`.btn-primary`, `.btn-outline`, `.btn-danger`) | Variants: primary / outline / danger; sizes md/sm; states default/hover/disabled/loading. Squared `0px` radius, `12px` / `11px` uppercase mono, `0.1em` tracking. | The button is a "mono label inside a squared box" — even primary actions feel like editorial captions rather than rounded CTAs. |
| Input | `preview/component-input.html` | `components/input.json` | `preview-only` | Renders as `input`, `textarea`, or `select`; states default/error/disabled. Label is meta-mono caption above field; error is `11px` mono destructive text. Field radius is the system exception at `4px`. | fztbucs prefers explicit stacked labels over floating labels; form fields read like labeled specimen rows. |
| Card | `preview/component-card.html` | `components/card.json` | `preview-only` | Optional header/body/footer anatomy; states default/hover; density default/minimal. Squared corners, `1px` `var(--border)` border, hover transitions border to `var(--primary)`. | Cards are flat, white editorial containers; elevation is reserved for overlays, never for cards. |
| Navbar | `preview/component-navbar.html` | `components/navbar.json` | `preview-only` | Fixed top flex row with brand, links, actions; light/dark theme; default/scrolled state. Links are `12px` mono uppercase with `0.05em` tracking; bottom border `1px` solid `var(--border)`. | The navbar is essentially a running header from a print publication — logo, mono nav labels, and one primary action. |
| Toast | `preview/component-toast.html` | `components/toast.json` | `preview-only` | Variants info/success/error; flex row with left `3px` accent border. Background `var(--card)`, text `13px` sans body. | Toasts use a colored left edge instead of a background tint, keeping the surface consistently white. |
| Avatar | `preview/component-avatar.html` | `components/avatar.json` | `preview-only` | Sizes sm/md/lg (`24px` / `40px` / `64px`); default/fallback states. Circular overflow with `muted` background and `muted-foreground` initials. | Avatar is the only circular element in the system; every other component is squared. |

---

## Index

- `README.md` — this file
- `colors_and_type.css` — CSS variables for color, type, radius, shadow, spacing
- `components.css` — aggregated component CSS extracted from preview pages (not present in this reconstruction; rely on `colors_and_type.css` for Button classes)
- `css.json` — structured token metadata
- `components/` — component contracts: `button.json`, `input.json`, `card.json`, `navbar.json`, `toast.json`, `avatar.json`
- `preview/` — small HTML cards for the Design System tab
- `ui_kits/{type}/` — full click-through recreation kits
- `SKILL.md` — agent skill manifest

---

## Caveats / known substitutions

1. **Fraunces and JetBrains Mono** are referenced via CSS variables (`--font-fraunces`, `--font-jetbrains`) but are not loaded by `colors_and_type.css`. We substitute **Noto Serif SC** for Fraunces and **SFMono-Regular / Menlo / Monaco** for JetBrains Mono when those variables are undefined. For pixel-perfect brand output, the consuming project must inject the actual Fraunces and JetBrains Mono font faces.
2. **Components other than Button** are documented from their JSON contracts only; no aggregated `components.css` or preview HTML evidence was available in the structured-spec extraction. CSS Source for these rows is listed as `preview-only`, meaning implementation details should be derived from the component contracts and the global tokens.
3. **This is a reconstruction from existing frontend code**, not a from-scratch Figma library. Some dimensions (for example, exact Input padding values noted as "encoded in the frontend utility file") were inferred from code patterns rather than observed in a design file.
4. **Concrete product UI copy** (button labels, form placeholders, empty-state text) was not present in the extracted structured spec. The copy examples above are drawn from CSS comments and component metadata; real product copy should follow the Chinese-first, editorial-technical voice described in Content Fundamentals.
