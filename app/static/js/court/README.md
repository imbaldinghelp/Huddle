# Court diagrams

Everything that draws a basketball court lives in this folder. The play page
(`../play-viewer.js`) and the court editor (`../play-editor.js`) both use it,
so a play always looks the same in both places.

## Files

| File | What it does |
|---|---|
| `court.js` | Draws the court lines. The only file that knows the court's shape and size. |
| `render.js` | Draws one diagram (players, ball, arrows) on top of the court. |
| `model.js` | Questions and changes about a diagram: who has the ball, where a move ends, the next step. |
| `animate.js` | Works out where everyone is part-way through a step, for the Play button. |
| `geometry.js` | Maths for lines: lengths, curves, zigzags. No drawing. |
| `svg.js` | Two small helpers for building SVG elements. |

Colours and line styles are not in the JavaScript. They are CSS classes in
`static/css/components.css` under "Court diagram".

## The diagram format

A play is a list of steps. Each step has a text `description` and a `diagram`,
which is saved in the database as JSON (`play_steps.diagram`):

```json
{
  "players": [
    {"id": "O1", "team": "offense", "x": 0.5,   "y": 0.65},
    {"id": "O2", "team": "offense", "x": 0.812, "y": 0.45},
    {"id": "O3", "team": "offense", "x": 0.188, "y": 0.45},
    {"id": "O4", "team": "offense", "x": 0.318, "y": 0.25},
    {"id": "O5", "team": "offense", "x": 0.682, "y": 0.25}
  ],
  "ball": {"holder": "O1"},
  "actions": [
    {"type": "pass", "from": "O1", "to": "O2"},
    {"type": "cut", "player": "O3", "path": [[0.3, 0.4], [0.45, 0.2]]},
    {"type": "screen", "player": "O5", "path": [[0.74, 0.4]]}
  ]
}
```

### Positions

`x` and `y` are fractions from 0 to 1, not pixels, so a diagram fits any
screen. They measure across the whole drawing: the half court plus a 1 metre
margin on every side (so an inbounder can stand out of bounds).

- `x`: 0 is the left edge, 1 is the right edge.
- `y`: 0 is the top edge (behind the baseline and basket), 1 is the bottom
  edge (just past the half-court line).

`toView()` in `court.js` turns a fraction into drawing units, and `fromView()`
goes back. One drawing unit is 10 cm on a real court.

### Players

- Attackers are `O1` to `O5` (drawn as circles numbered 1 to 5). All five are
  always there.
- Defenders are `X1` to `X5` (drawn as X1 to X5). They are optional, but it is
  all five or none, and every step of a play shows the same players.
- `team` is `"offense"` or `"defense"`.

### Ball

`ball.holder` is the id of the attacker who has the ball at the start of the
step.

### Actions

What happens during the step. Each player can have one move, and there can be
one pass.

| `type` | Fields | Drawn as |
|---|---|---|
| `cut` | `player`, `path` | solid line with an arrowhead |
| `dribble` | `player`, `path` | zigzag line with an arrowhead |
| `screen` | `player`, `path` | solid line ending in a short bar |
| `pass` | `from`, `to` | dashed line with an arrowhead |

- `path` is the list of points the player moves through, **after** their
  starting position. The last point is where they end up. It holds 1 to 12
  points, and the line is drawn as a smooth curve through them.
- Only the player with the ball can `dribble`.
- A `pass` goes `from` the player with the ball `to` another attacker.
- Timing of a pass: a passer who also dribbles passes at the end of the
  dribble. A passer who cuts passes first, then cuts. The receiver catches the
  ball where their own move ends.

### From one step to the next

When the editor adds a step, `nextDiagram()` in `model.js` builds it: every
player stands where their move ended, the ball is with whoever caught the
pass, and there are no arrows yet.

## Where the rules are checked

The browser is never trusted. When a play is saved, the server checks every
value again in `app/playbook/validation.py` (ids, positions between 0 and 1,
sizes, the rules above) and rebuilds the diagram from the checked values only.
**If you change the format here, change that file and its tests
(`tests/test_play_validation.py`) too.**

## Adding a full court later

Only `court.js` knows the court's shape. To add a full court: draw a second
set of lines there, make `VIEW` depend on which court is in use, and store
which court a play uses (for example a `"court": "full"` field in each
diagram, checked in `validation.py`).
