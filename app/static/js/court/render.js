// Draws one diagram (players, ball and arrows) into the court's diagram layer.
// The viewer and the editor both use this, so a play looks the same in both.
// Colours and line styles come from CSS (components.css, "Court diagram").

import { toView } from "./court.js";
import { distance, endDirection, pathLength, slicePath, zigzag } from "./geometry.js";
import { findPlayer, moveLine, passLine } from "./model.js";
import { pathData, svgElement } from "./svg.js";

// Sizes in drawing units (1 unit = 10 cm on a real court).
export const PLAYER_RADIUS = 6;
const LINE_GAP = 1.5; // space between a marker and a line that touches it
const ARROW_LENGTH = 5.5;
const ARROW_WIDTH = 4.6;
const SCREEN_BAR = 9;
const ZIGZAG_HEIGHT = 2.1;
const ZIGZAG_STEP = 4;
export const BALL_OFFSET = 4.8; // the ball sits at the lower right of its holder

// options.positions  { O1: [x, y] }  draw these players somewhere else (animation)
// options.ballAt     [x, y] in drawing units: draw the ball mid-flight (animation)
export function renderDiagram(layer, diagram, options = {}) {
  const positions = options.positions ?? {};
  const centreOf = (player) => toView(positions[player.id] ?? [player.x, player.y]);

  const holder = findPlayer(diagram, diagram.ball.holder);
  const ballCentre = options.ballAt ?? (holder ? centreOf(holder) : null);

  layer.replaceChildren(
    ...diagram.actions.map((action, index) => drawAction(diagram, action, index)),
    ...diagram.players.map((player) => drawPlayer(player, centreOf(player))),
    ...(ballCentre ? [drawBall(ballCentre)] : []),
  );
}

function drawPlayer(player, [x, y]) {
  const number = player.id.slice(1);
  const label =
    player.team === "offense"
      ? svgElement("text", { dy: "0.35em" }, [number])
      : svgElement("text", { dy: "0.35em" }, ["X", svgElement("tspan", { class: "court-player-sub", dy: "1.6" }, [number])]);

  return svgElement(
    "g",
    {
      class: `court-player court-player-${player.team}`,
      transform: `translate(${x.toFixed(2)} ${y.toFixed(2)})`,
      "data-player-id": player.id,
    },
    [svgElement("circle", { r: PLAYER_RADIUS }), label],
  );
}

function drawBall([x, y]) {
  return svgElement("circle", {
    class: "court-ball",
    cx: (x + BALL_OFFSET).toFixed(2),
    cy: (y + BALL_OFFSET).toFixed(2),
    r: 2.8,
    "data-ball": "",
  });
}

function drawAction(diagram, action, index) {
  // A defender's arrows are drawn in the defenders' colour.
  const team = action.player?.startsWith("X") ? " court-action-defense" : "";
  const group = svgElement("g", {
    class: `court-action court-action-${action.type}${team}`,
    "data-action-index": index,
  });

  // Every line starts just outside the marker of the player it belongs to.
  if (action.type === "pass") {
    const [start, end] = passLine(diagram);
    const line = slicePath([start, end], PLAYER_RADIUS + LINE_GAP, distance(start, end) - PLAYER_RADIUS - LINE_GAP);
    addArrow(group, line);
    return group;
  }

  const full = moveLine(diagram, action);
  const line = slicePath(full, PLAYER_RADIUS + LINE_GAP, pathLength(full));
  if (action.type === "screen") {
    addScreen(group, line);
  } else if (action.type === "dribble") {
    addArrow(group, zigzagWithStraightEnd(line));
  } else {
    addArrow(group, line);
  }
  return group;
}

// The zigzag stops a little early so the arrowhead sits on a straight piece.
function zigzagWithStraightEnd(line) {
  const body = slicePath(line, 0, pathLength(line) - ARROW_LENGTH - 2);
  if (body.length < 2) {
    return line;
  }
  return [...zigzag(body, ZIGZAG_HEIGHT, ZIGZAG_STEP), line[line.length - 1]];
}

// A line with a filled triangle at its end: cuts, dribbles and passes.
function addArrow(group, line) {
  if (line.length < 2) {
    return;
  }
  const tip = line[line.length - 1];
  const [dx, dy] = endDirection(line);
  const back = [tip[0] - dx * ARROW_LENGTH, tip[1] - dy * ARROW_LENGTH];
  const half = ARROW_WIDTH / 2;
  const corners = [tip, [back[0] - dy * half, back[1] + dx * half], [back[0] + dy * half, back[1] - dx * half]];
  // The line ends inside the triangle so its blunt end does not poke through the tip.
  const shaft = slicePath(line, 0, pathLength(line) - ARROW_LENGTH * 0.8);

  group.append(
    svgElement("path", { class: "court-action-hit", d: pathData(line) }),
    svgElement("path", { class: "court-action-line", d: pathData(shaft.length > 1 ? shaft : line) }),
    svgElement("polygon", {
      class: "court-action-head",
      points: corners.map(([x, y]) => `${x.toFixed(2)},${y.toFixed(2)}`).join(" "),
    }),
  );
}

// A line ending in a short bar across it: a screen.
function addScreen(group, line) {
  if (line.length < 2) {
    return;
  }
  const end = line[line.length - 1];
  const [dx, dy] = endDirection(line);
  const half = SCREEN_BAR / 2;
  const bar = [
    [end[0] - dy * half, end[1] + dx * half],
    [end[0] + dy * half, end[1] - dx * half],
  ];
  group.append(
    svgElement("path", { class: "court-action-hit", d: pathData(line) }),
    svgElement("path", { class: "court-action-line", d: pathData(line) }),
    svgElement("path", { class: "court-action-line court-action-bar", d: pathData(bar) }),
  );
}
