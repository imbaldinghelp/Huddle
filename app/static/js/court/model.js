// Questions and changes about one diagram: who is where, who has the ball,
// where a move ends. The diagram format is described in README.md.

import { BASKET, fromView, toView } from "./court.js";
import { distance, lerp, smooth } from "./geometry.js";

export const OFFENSE_IDS = ["O1", "O2", "O3", "O4", "O5"];
export const DEFENSE_IDS = ["X1", "X2", "X3", "X4", "X5"];

// How far in front of an attacker a new defender stands (drawing units).
const DEFENDER_GAP = 13;

// The first step of a new play: three players outside, two by the basket.
export function startingDiagram() {
  return {
    players: [
      { id: "O1", team: "offense", x: 0.5, y: 0.65 },
      { id: "O2", team: "offense", x: 0.812, y: 0.45 },
      { id: "O3", team: "offense", x: 0.188, y: 0.45 },
      { id: "O4", team: "offense", x: 0.318, y: 0.25 },
      { id: "O5", team: "offense", x: 0.682, y: 0.25 },
    ],
    ball: { holder: "O1" },
    actions: [],
  };
}

export function findPlayer(diagram, id) {
  return diagram.players.find((player) => player.id === id);
}

// A player's cut, dribble or screen in this step, if they have one.
export function findMove(diagram, playerId) {
  return diagram.actions.find((action) => action.type !== "pass" && action.player === playerId);
}

export function findPass(diagram) {
  return diagram.actions.find((action) => action.type === "pass");
}

// Where a player stands once this step's move is finished.
export function endPosition(diagram, player) {
  const move = findMove(diagram, player.id);
  return move ? move.path[move.path.length - 1] : [player.x, player.y];
}

// The curve a move follows, in drawing units, starting at the player.
export function moveLine(diagram, move) {
  const player = findPlayer(diagram, move.player);
  return smooth([[player.x, player.y], ...move.path].map(toView));
}

// Where a pass starts and ends, in drawing units.
// A passer who dribbles passes at the end of the dribble; one who cuts passes
// first, then cuts. The receiver catches the ball where their own move ends.
export function passLine(diagram) {
  const pass = findPass(diagram);
  const passer = findPlayer(diagram, pass.from);
  const receiver = findPlayer(diagram, pass.to);
  const dribbles = findMove(diagram, passer.id)?.type === "dribble";
  const start = dribbles ? endPosition(diagram, passer) : [passer.x, passer.y];
  return [toView(start), toView(endPosition(diagram, receiver))];
}

// The diagram a new step starts from: everyone where the last step left them.
export function nextDiagram(diagram) {
  const pass = findPass(diagram);
  return {
    players: diagram.players.map((player) => {
      const [x, y] = endPosition(diagram, player);
      return { ...player, x, y };
    }),
    ball: { holder: pass ? pass.to : diagram.ball.holder },
    actions: [],
  };
}

// Hands the ball to a player. A pass or dribble drawn for the old ball
// handler no longer makes sense, so those arrows are removed.
export function giveBall(diagram, playerId) {
  diagram.ball.holder = playerId;
  diagram.actions = diagram.actions.filter((action) => action.type !== "pass" && action.type !== "dribble");
}

export function hasDefenders(diagram) {
  return diagram.players.some((player) => player.team === "defense");
}

// Adds X1 to X5, each standing between their attacker and the basket.
export function addDefenders(diagram) {
  if (hasDefenders(diagram)) {
    return;
  }
  OFFENSE_IDS.forEach((offenseId, index) => {
    const player = findPlayer(diagram, offenseId);
    const attacker = toView([player.x, player.y]);
    const gap = distance(attacker, BASKET);
    // An attacker right under the basket gets their defender just below them.
    const spot =
      gap > DEFENDER_GAP * 1.5
        ? lerp(attacker, BASKET, DEFENDER_GAP / gap)
        : [attacker[0], attacker[1] + DEFENDER_GAP];
    const [x, y] = fromView(spot);
    diagram.players.push({ id: DEFENSE_IDS[index], team: "defense", x, y });
  });
}

export function removeDefenders(diagram) {
  diagram.players = diagram.players.filter((player) => player.team !== "defense");
  diagram.actions = diagram.actions.filter((action) => !DEFENSE_IDS.includes(action.player));
}
