---
name: Huddle
description: A private basketball playbook for SUTD Basketball.
colors:
  court-orange: "#e45b35"
  court-orange-deep: "#c54625"
  locker-green: "#435d4c"
  marker-ink: "#18231f"
  ink-soft: "#39463f"
  muted-grey: "#656c64"
  board-white: "#fffefa"
  paper: "#f2f1eb"
  rule-line: "#d9d9d0"
  field-line: "#7d857b"
  track-grey: "#e9e9e1"
  photo-green: "#283b32"
  alert-tint: "#fff0e9"
  alert-text: "#87391f"
  arrow-peach: "#f39a73"
  success-tint: "#e6eee8"
  success-text: "#2f4a39"
  selection-peach: "#f6cfc0"
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
  page-title:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "48px"
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
  input:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "16px"
    fontWeight: 400
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
    textColor: "{colors.board-white}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "0 17px"
    height: "52px"
  button-primary-hover:
    backgroundColor: "{colors.locker-green}"
  button-compact:
    backgroundColor: "{colors.marker-ink}"
    textColor: "{colors.board-white}"
    rounded: "{rounded.none}"
    padding: "0 18px"
    height: "44px"
  button-quiet:
    backgroundColor: "{colors.board-white}"
    textColor: "{colors.marker-ink}"
    rounded: "{rounded.none}"
    padding: "0 18px"
    height: "44px"
  tag:
    backgroundColor: "{colors.locker-green}"
    textColor: "{colors.board-white}"
    rounded: "{rounded.none}"
    padding: "3px 7px"
  input-field:
    backgroundColor: "{colors.board-white}"
    textColor: "{colors.marker-ink}"
    typography: "{typography.input}"
    rounded: "{rounded.none}"
    padding: "0 14px"
    height: "50px"
  segmented-option:
    backgroundColor: "{colors.track-grey}"
    textColor: "{colors.ink-soft}"
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
    textColor: "{colors.board-white}"
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
- **Muted Grey** (`muted-grey`, CSS `--muted`): small supporting text such as dates and placeholders. It passes AA on both Board White and Paper.
- **Board White** (`board-white`, CSS `--white`): the main working surface and text on dark areas.
- **Paper** (`paper`, CSS `--paper`): the page background behind the board.
- **Rule Line** (`rule-line`, CSS `--line`): dividers.
- **Field Line** (`field-line`, CSS `--field-line`): borders of inputs and quiet buttons. Dark enough (3:1) to show where a control is.
- **Track Grey** (`track-grey`, CSS `--track`): the track behind segmented options and quiet tags.
- **Photo Green** (`photo-green`, CSS `--photo-green`): the fallback colour behind the team photo.
- **Alert Tint / Alert Text** (`alert-tint`, `alert-text`): background and text of error messages.
- **Success Tint / Success Text** (`success-tint`, `success-text`): background and text of confirmation messages.
- **Arrow Peach** (`arrow-peach`): the arrow on the dark primary button only.
- **Selection Peach** (`selection-peach`, CSS `--selection`): highlighted text.

### Named Rules
**The One Marker Rule.** Orange is the only loud colour. It marks one or two small things per screen (brand mark, focus, an alert edge). It is never a page background, a card fill or a gradient.

**The Tokens Only Rule.** Colours, fonts and shadows are defined in `app/static/css/tokens.css` and used through `var(--name)`. The one exception is the dark gradient over the login photo, which lives in `pages/login.css`.

## Typography

**Display Font:** Barlow Condensed (with Arial Narrow, sans-serif)
**Body Font:** DM Sans (with sans-serif)

**Character:** A scoreboard over a notebook. The condensed face is loud and tall for the few words that name a page; DM Sans is small and even for everything a player actually reads.

### Hierarchy
- **Display** (600, 76px, line-height 0.91; 64px under 1000px, 43px under 720px): the one big statement on a photo or hero area.
- **Headline** (600, 54px, line-height 1; 48px under 720px): the page heading, for example "Welcome back."
- **Page title** (600, 48px, line-height 1; 40px under 720px): the heading of every logged-in page, for example "Players"
- **Title** (700, 25px, line-height 0.95): the HUDDLE wordmark (22px in the header); the size for card and section titles.
- **Body** (400, 13px to 14px, line-height 1.6): descriptions, notes, list text.
- **Input** (400, 16px): text typed into fields. 16px stops iPhones from zooming in on focus.
- **Label** (700, 12px): field labels and button text. Segmented options use 600.
- **Kicker** (700, 10px, typed in capitals): the "TEAM ACCESS" label on the login page. Footer text uses the same style at 9px. Tags use 11px bold.

### Named Rules
**The Two Voices Rule.** Barlow Condensed is for headings and the wordmark only. Anything longer than a short line, and every control, is DM Sans.

**The Capitals Are Typed Rule.** Kickers and the wordmark are written in capitals in the HTML. There is no `text-transform` and no extra letter-spacing.

## Layout

The login page is a two-panel split: team photo on the left (1.08 parts), the board on the right (0.92 parts, at least 440px), full viewport height, capped at 1680px wide. The form sits in a 390px column, centred in its panel.

- **Under 1000px:** the panels become roughly equal and padding tightens (48px/64px down to 36px/42px).
- **Under 720px:** the panels stack. The photo becomes a 265px banner on top and the form fills the rest with 24px side padding.
- **Under 380px:** side padding drops to 19px. The minimum supported width is 320px.

Logged-in pages share one shell: a 60px Board White header with a bottom Rule Line, then the content on Paper in a 960px column with 24px side padding (16px under 420px). Form pages use a narrow 438px column so the form is 390px wide, the same as on the login page. The playbook's category and list pages use a medium 768px column (`.page-medium`). The play page and court editor use the full column: court on the left, text or steps on the right, stacking into one column under 860px. Lists sit in a Board White block with 1px Rule Line borders; on phones each row stacks into one column.

Spacing follows the form's rhythm: 4px inside controls, 10px between a label and its field, 14px inside fields, 26px between form groups, 38px between a heading and the form, 48px as panel padding. Controls are tall enough to tap: 42px options, 50px fields, 52px buttons.

## Elevation & Depth

Mostly flat. Surfaces are separated by tone (Board White on Paper, Track Grey behind options) and by thin 1px lines. Light shadows are allowed, kept soft and tinted with Marker Ink, to show that something is selected or sits above the page (a selected option, a card, a menu). Depth on the photo comes from a dark gradient wash that keeps white text readable.

### Shadow Vocabulary
- **Selected lift** (`box-shadow: 0 1px 4px rgba(24, 35, 31, 0.12)`, CSS `--shadow-lift`): the selected segmented option. Use the same strength for raised cards.
- **Focus glow** (`box-shadow: 0 0 0 3px rgba(67, 93, 76, 0.24)`, CSS `--focus-glow`): the ring around a focused field, with a Locker Green border.

### Named Rules
**The Light Touch Rule.** A shadow is never darker than 12% Marker Ink and never wider than a few pixels. If a surface needs a heavy shadow to stand out, change its background tone or add a line.

## Shapes

Square. Every button, field, option, message and the brand mark has a 0 radius. The only circles are small dots (6px to 7px) and, later, players on the court diagram. Borders are 1px; the one thick line is the 3px orange edge on a form message. The board surface carries a faint dot grid (0.65px dots, 17px apart, 7% Marker Ink).

## Components

### Buttons
- **Shape:** square (0 radius), full width of the form, 52px tall.
- **Primary:** Marker Ink background, Board White 13px bold label on the left, Arrow Peach arrow on the right, 17px side padding.
- **Hover / Focus:** background changes to Locker Green over 160ms and the arrow moves 3px right. Focus shows a 2px Court Orange outline, 3px away from the button.
- **Compact:** 44px tall, 18px side padding, Marker Ink background, no arrow. For page actions such as "Add player" and links that act as buttons. Sizes to its label.
- **Quiet:** the compact button in Board White with a Field Line border and Marker Ink text; the border turns Marker Ink on hover. For secondary and repeated actions such as "Reset password" in a list.
- **Text button:** no background, Locker Green 12px bold text (Show/Hide); Court Orange Deep on hover.

### Segmented Options
- **Style:** two equal options on a Track Grey track with 4px padding and a 3px gap. Each option is 42px tall, 12px, weight 600, Ink Soft text. Class `.segmented`; not used on a page yet.
- **State:** the selected option turns Board White with Marker Ink text and the Selected lift shadow. Keyboard focus shows a 2px Court Orange outline.

### Inputs / Fields
- **Style:** a 12px bold label above a Board White box with a 1px Field Line border, square, 50px tall, 16px text, 14px side padding. An action such as Show/Hide can sit inside the field on the right. Build fields with the `text_field` macro in `templates/components/forms.html`.
- **Hint:** 12px Ink Soft text under the field.
- **Focus:** the border turns Locker Green with the Focus glow ring.
- **Error:** the border turns Court Orange Deep and a 12px bold Alert Text message replaces the hint. An error that belongs to the whole form (for example a wrong login) is a form message above the button.

### Form Message
- **Error:** Alert Tint background, Alert Text 13px text, 3px Court Orange left edge, 10px by 12px padding, `role="alert"`.
- **Success:** Success Tint background, Success Text, Locker Green left edge. Used for confirmations at the top of a page ("Kai Chen has been reactivated.").

### Brand Lockup
- **Style:** a 42px Court Orange square with a white condensed "H", next to the HUDDLE wordmark (25px, weight 700) and a 9px bold subtitle. On phones the square is 36px and the wordmark 22px.

### Site Header
- **Style:** 60px tall, Board White, 1px Rule Line below. Compact brand lockup on the left (36px mark, 22px wordmark); on the right the Admin link (admins only), the user's name (links to Change password) and Logout, all 13px weight 600.
- **State:** the current section has a 3px Court Orange line on the header's bottom edge. Hover underlines the link in Court Orange. Long names are cut with an ellipsis.

### Tag
- **Style:** 11px bold, 3px by 7px padding, square. Locker Green with Board White text for a role ("Admin"); Track Grey with Ink Soft text for a state ("Deactivated", "Temporary password").

### List Rows
- **Style:** rows inside one Board White block with a 1px Rule Line border and 1px lines between rows; 14px by 18px padding. The main text is 14px weight 600, supporting text 13px or 12px Muted Grey. Columns line up across rows; on phones a row stacks. Classes `.row-list`, `.row`, `.row-title`, `.row-sub`, `.row-meta` in `components.css`.
- **As links:** in the playbook each row is one link (`.play-link`); it turns Paper on hover.
- **Empty:** when a list has nothing in it, a short `.empty-note` says what will appear there and how.

### Category Card
- **Style:** the four playbook categories as square Board White cards, two per row at every width, with a 1px Rule Line border. A Marker Ink icon sits above the name (Barlow Condensed 30px, 22px on phones, Locker Green) and the play count (13px Muted Grey).
- **State:** on hover the border turns Marker Ink and the card gets the Selected lift shadow.

### Chat (Ask About This Play)
- **Where:** on the play page, in the right column under the step description and legend (under the court on phones). On wide, tall screens the court stays in view while this column scrolls. Not shown on drafts.
- **Style:** a Barlow Condensed 25px heading with a 12px Muted Grey count of the questions left, over a Board White panel with a 1px Rule Line border. Messages are turns, like a chat app, in Huddle's own shapes: your message sits on the right in a square Track Grey block; the reply is plain 14px Ink Soft text on the left. The conversation scrolls inside the panel (420px at most) and the question box stays at the bottom: a normal field with a 42px Send button inside it.
- **States:** before the first message, a short note and three ready-made questions as square outlined buttons. While a reply loads, three 6px Muted Grey dots pulse (still under reduced motion) and Send is disabled. A failed reply puts the question back in the box and shows an error form message above it. When the day's questions are used up, a quiet note replaces the question box.

### Breadcrumbs
- **Style:** the trail at the top of every page below a top-level one ("Playbook / Offense / Horns Flare"), 13px weight 600 on a Rule Line, the same strip as the section tabs. Links are Marker Ink and underlined (Court Orange Deep on hover), separated by a Muted Grey slash; the current page is Muted Grey and not a link. Each link is 44px tall. Build it with the `breadcrumbs` macro in `templates/components/breadcrumbs.html`. It replaces the old small "Back to ..." links.

### Icons
- **Style:** line icons drawn for Huddle, with square ends and filled arrowheads, like the court diagram. Files in `app/static/icons/`, shown through the `.icon` class, which paints them in the current text colour.

### Court Diagram
- **Style:** a Board White court with Field Line markings, a Paper key and an Ink Soft boundary. Attackers are Board White circles with a Marker Ink outline and number. Defenders are a Locker Green X with a small number. Arrows are Marker Ink: solid for a cut, dashed for a pass, zigzag for a dribble, a bar across the end for a screen.
- **The ball** is a small Court Orange dot on its holder. It is the one orange mark on the court.
- **Step marks:** a row of thin bars under the court, one per step; the current step is Court Orange.

### Toolbar
- **Style:** the editor's drawing tools sit on a Track Grey track like segmented options: 42px tall, icon plus a 12px weight 600 label. The chosen tool turns Board White with the Selected lift shadow. The steps list uses the same track and lift for the current step.

### Kicker Label
- **Style:** 10px bold capitals in Locker Green above the login heading. Login page only: on every other page the heading stands alone.

## Do's and Don'ts

### Do:
- **Do** use the colours and fonts from `tokens.css` through `var(--name)`.
- **Do** keep every corner square (0 radius).
- **Do** put one Barlow Condensed heading on a page and let DM Sans do the rest.
- **Do** keep controls at least 42px tall so they are easy to tap on a phone.
- **Do** keep the 2px Court Orange focus outline on anything that can be focused.
- **Do** respect `prefers-reduced-motion`; transitions are 160ms and only change colour or nudge position.
- **Do** keep text at WCAG AA contrast (4.5:1). Marker Ink, Ink Soft, Locker Green and Muted Grey all pass on Board White and Paper. Court Orange does not pass as text: use Court Orange Deep or Alert Text.
- **Do** give repeated buttons a full `aria-label` ("Deactivate Wei Jie"), so screen readers can tell the rows apart.

### Don't:
- **Don't** use purple, gradients as decoration, or any accent colour other than Court Orange.
- **Don't** use emoji as icons; icons are custom SVGs in `app/static/icons/`.
- **Don't** round corners or turn buttons into pills.
- **Don't** use heavy or coloured drop shadows.
- **Don't** set body text, labels or controls in Barlow Condensed.
- **Don't** use pure black (`#000`) or pure white (`#fff`) for surfaces.
- **Don't** fill large areas with Court Orange.
- **Don't** add a kicker label above headings on new pages.
- **Don't** set field text below 16px.
