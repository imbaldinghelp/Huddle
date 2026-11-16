---
name: Huddle
description: A private basketball playbook for SUTD Basketball.
colors:
  court-orange: "#e45b35"
  court-orange-deep: "#c54625"
  locker-green: "#435d4c"
  marker-ink: "#18231f"
  ink-soft: "#39463f"
  muted-grey: "#70776f"
  board-white: "#fffefa"
  paper: "#f2f1eb"
  rule-line: "#d9d9d0"
  field-line: "#cfd2c9"
  track-grey: "#e9e9e1"
  photo-green: "#283b32"
  alert-tint: "#fff0e9"
  alert-text: "#87391f"
  arrow-peach: "#f39a73"
typography:
  display:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "76px"
    fontWeight: 600
    lineHeight: 0.91
  headline:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "54px"
    fontWeight: 600
    lineHeight: 1
  title:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "25px"
    fontWeight: 700
    lineHeight: 0.95
  body:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "12px"
    fontWeight: 700
  kicker:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "10px"
    fontWeight: 700
rounded:
  none: "0"
spacing:
  xs: "4px"
  sm: "10px"
  md: "14px"
  lg: "26px"
  xl: "38px"
  panel: "48px"
components:
  button-primary:
    backgroundColor: "{colors.marker-ink}"
    textColor: "#ffffff"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "0 17px"
    height: "52px"
  button-primary-hover:
    backgroundColor: "{colors.locker-green}"
  input-field:
    backgroundColor: "{colors.board-white}"
    textColor: "{colors.marker-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: "0 14px"
    height: "50px"
  segmented-option:
    backgroundColor: "{colors.track-grey}"
    textColor: "#69716a"
    rounded: "{rounded.none}"
    padding: "8px 10px"
    height: "42px"
  segmented-option-selected:
    backgroundColor: "{colors.board-white}"
    textColor: "{colors.marker-ink}"
  form-message:
    backgroundColor: "{colors.alert-tint}"
    textColor: "{colors.alert-text}"
    rounded: "{rounded.none}"
    padding: "10px 12px"
  brand-mark:
    backgroundColor: "{colors.court-orange}"
    textColor: "#ffffff"
    rounded: "{rounded.none}"
    size: "42px"
---

# Design System: Huddle

## Overview

**Creative North Star: "The Locker Room Whiteboard"**

Huddle looks like the board the team gathers around before a game: an off-white surface, dark marker ink, one orange marker for the thing that matters. It is made for the team only, so nothing on it is selling anything. Headings are tall and condensed like a scoreboard; everything else is small, plain and quiet.

The mood is focused and no-nonsense. A player opens Huddle to learn a play, usually on a phone, often minutes before training. Pages are calm, sharp and practical. Edges are square. Colour is used sparingly, and decoration is limited to one faint dot grid on the board surface and the team photo on the login page.

**Key Characteristics:**
- Off-white board surface with dark green-black ink, never pure white or pure black.
- Tall condensed headings (Barlow Condensed) over small, plain body text (DM Sans).
- Square corners everywhere (0 radius).
- One orange accent, used in small amounts.
- Mostly flat surfaces; light shadows are allowed where they help show what is raised or selected.

## Colors

A warm paper-and-ink palette with a deep court green and one orange accent. Every neutral is tinted slightly green-grey so nothing looks sterile.

### Primary
- **Court Orange** (`court-orange`, CSS `--orange`): the brand mark, focus outlines, the left edge of form messages, small dividers. An accent, not a fill for large areas.
- **Court Orange Deep** (`court-orange-deep`, CSS `--orange-dark`): hover colour for orange or green text links.

### Secondary
- **Locker Green** (`locker-green`, CSS `--green`): kicker labels, text buttons such as Show/Hide, the focused field border, and the hover state of the primary button.

### Neutral
- **Marker Ink** (`marker-ink`, CSS `--ink`): main text and the primary button.
- **Ink Soft** (`ink-soft`, CSS `--ink-soft`): secondary text that still needs to read clearly.
- **Muted Grey** (`muted-grey`, CSS `--muted`): helper text and notes.
- **Board White** (`board-white`, CSS `--white`): the main working surface and text on dark areas.
- **Paper** (`paper`, CSS `--paper`): the page background behind the board.
- **Rule Line** (`rule-line`, CSS `--line`): dividers.
- **Field Line** (`field-line`): input borders.
- **Track Grey** (`track-grey`): the track behind segmented options.
- **Photo Green** (`photo-green`): the fallback colour behind the team photo.
- **Alert Tint / Alert Text** (`alert-tint`, `alert-text`): background and text of form messages.
- **Arrow Peach** (`arrow-peach`): the arrow on the dark primary button only.

### Named Rules
**The One Marker Rule.** Orange is the only loud colour. It marks one or two small things per screen (brand mark, focus, an alert edge). It is never a page background, a card fill or a gradient.

**The Tokens Only Rule.** Colours and fonts are defined in `app/static/css/tokens.css` and used through `var(--name)`. Several neutrals above are still written as hex values in the login CSS; move them into `tokens.css` the first time a second page needs them.

## Typography

**Display Font:** Barlow Condensed (with Arial Narrow, sans-serif)
**Body Font:** DM Sans (with sans-serif)

**Character:** A scoreboard over a notebook. The condensed face is loud and tall for the few words that name a page; DM Sans is small and even for everything a player actually reads.

### Hierarchy
- **Display** (600, 76px, line-height 0.91; 64px under 1000px, 43px under 720px): the one big statement on a photo or hero area.
- **Headline** (600, 54px, line-height 1; 48px under 720px): the page heading, for example "Welcome back."
- **Title** (700, 25px, line-height 0.95): the HUDDLE wordmark; the size for card and section titles.
- **Body** (400, 13px to 14px, line-height 1.6): descriptions, notes, field text.
- **Label** (700, 12px): field labels and button text. Segmented options use 600.
- **Kicker** (700, 10px, typed in capitals): small labels above a heading, such as "TEAM ACCESS". Footer text uses the same style at 9px.

### Named Rules
**The Two Voices Rule.** Barlow Condensed is for headings and the wordmark only. Anything longer than a short line, and every control, is DM Sans.

**The Capitals Are Typed Rule.** Kickers and the wordmark are written in capitals in the HTML. There is no `text-transform` and no extra letter-spacing.

## Layout

The login page is a two-panel split: team photo on the left (1.08 parts), the board on the right (0.92 parts, at least 440px), full viewport height, capped at 1680px wide. The form sits in a 390px column, centred in its panel.

- **Under 1000px:** the panels become roughly equal and padding tightens (48px/64px down to 36px/42px).
- **Under 720px:** the panels stack. The photo becomes a 265px banner on top and the form fills the rest with 24px side padding.
- **Under 380px:** side padding drops to 19px. The minimum supported width is 320px.

Spacing follows the form's rhythm: 4px inside controls, 10px between a label and its field, 14px inside fields, 26px between form groups, 38px between a heading and the form, 48px as panel padding. Controls are tall enough to tap: 42px options, 50px fields, 52px buttons.

## Elevation & Depth

Mostly flat. Surfaces are separated by tone (Board White on Paper, Track Grey behind options) and by thin 1px lines. Light shadows are allowed, kept soft and tinted with Marker Ink, to show that something is selected or sits above the page (a selected option, a card, a menu). Depth on the photo comes from a dark gradient wash that keeps white text readable.

### Shadow Vocabulary
- **Selected lift** (`box-shadow: 0 1px 4px rgba(24, 35, 31, 0.12)`): the selected segmented option. Use the same strength for raised cards.
- **Focus glow** (`box-shadow: 0 0 0 3px rgba(67, 93, 76, 0.12)`): the ring around a focused field, with a Locker Green border.

### Named Rules
**The Light Touch Rule.** A shadow is never darker than 12% Marker Ink and never wider than a few pixels. If a surface needs a heavy shadow to stand out, change its background tone or add a line.

## Shapes

Square. Every button, field, option, message and the brand mark has a 0 radius. The only circles are small dots (6px to 7px) and, later, players on the court diagram. Borders are 1px; the one thick line is the 3px orange edge on a form message. The board surface carries a faint dot grid (0.65px dots, 17px apart, 7% Marker Ink).

## Components

### Buttons
- **Shape:** square (0 radius), full width of the form, 52px tall.
- **Primary:** Marker Ink background, white 12px bold label on the left, Arrow Peach arrow on the right, 17px side padding.
- **Hover / Focus:** background changes to Locker Green over 160ms and the arrow moves 3px right. Focus shows a 2px Court Orange outline, 3px away from the button.
- **Text button:** no background, Locker Green 11px bold text (Show/Hide); Court Orange Deep on hover.

### Segmented Options
- **Style:** two equal options on a Track Grey track with 4px padding and a 3px gap. Each option is 42px tall, 12px, weight 600, grey text.
- **State:** the selected option turns Board White with Marker Ink text and the Selected lift shadow. Keyboard focus shows a 2px Court Orange outline.

### Inputs / Fields
- **Style:** Board White, 1px Field Line border, square, 50px tall, 13px text, 14px side padding. An action such as Show/Hide can sit inside the field on the right.
- **Focus:** the border turns Locker Green with the Focus glow ring.
- **Error:** shown below the field as a form message, not as a red border.

### Form Message
- **Style:** Alert Tint background, Alert Text 12px text, 3px Court Orange left edge, 10px by 12px padding, `role="alert"`.

### Brand Lockup
- **Style:** a 42px Court Orange square with a white condensed "H", next to the HUDDLE wordmark (25px, weight 700) and a 9px bold subtitle. On phones the square is 36px and the wordmark 22px.

### Kicker Label
- **Style:** 10px bold capitals in Locker Green above a heading. An orange dot or span may sit beside it.

## Do's and Don'ts

### Do:
- **Do** use the colours and fonts from `tokens.css` through `var(--name)`.
- **Do** keep every corner square (0 radius).
- **Do** put one Barlow Condensed heading on a page and let DM Sans do the rest.
- **Do** keep controls at least 42px tall so they are easy to tap on a phone.
- **Do** keep the 2px Court Orange focus outline on anything that can be focused.
- **Do** respect `prefers-reduced-motion`; transitions are 160ms and only change colour or nudge position.
- **Do** check contrast on new pages. Small grey text (9px to 10px footer and kicker text, placeholder text) and orange text on Board White are below WCAG AA today; use Marker Ink, Ink Soft or Locker Green for text people need to read.

### Don't:
- **Don't** use purple, gradients as decoration, or any accent colour other than Court Orange.
- **Don't** use emoji as icons; icons are custom SVGs in `app/static/icons/`.
- **Don't** round corners or turn buttons into pills.
- **Don't** use heavy or coloured drop shadows.
- **Don't** set body text, labels or controls in Barlow Condensed.
- **Don't** use pure black (`#000`) or pure white (`#fff`) for surfaces.
- **Don't** fill large areas with Court Orange.
