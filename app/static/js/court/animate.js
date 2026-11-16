// Works out where everyone is part-way through a step, for the viewer's
// "Play" button. It only does the maths; play-viewer.js runs the clock.

import { fromView } from "./court.js";
import { lerp, pointAlong } from "./geometry.js";
import { findMove, findPass, moveLine, passLine } from "./model.js";

// When the passer dribbles first, the dribble takes this share of the step
// and the pass takes the rest.
const DRIBBLE_SHARE = 0.6;

// progress runs from 0 (step starts) to 1 (step finished).
// Returns { positions, ballAt } in the form renderDiagram() accepts.
export function frameAt(diagram, progress) {
  const pass = findPass(diagram);
  const dribbleThenPass = pass && findMove(diagram, pass.from)?.type === "dribble";

  const moveProgress = dribbleThenPass ? progress / DRIBBLE_SHARE : progress;
  const passProgress = dribbleThenPass ? (progress - DRIBBLE_SHARE) / (1 - DRIBBLE_SHARE) : progress;

  const positions = {};
  for (const action of diagram.actions) {
    if (action.type !== "pass") {
      positions[action.player] = fromView(pointAlong(moveLine(diagram, action), ease(moveProgress)));
    }
  }

  // Until the pass leaves, the ball simply stays with its holder.
  let ballAt = null;
  if (pass && passProgress > 0) {
    const [start, end] = passLine(diagram);
    ballAt = lerp(start, end, ease(passProgress));
  }
  return { positions, ballAt };
}

// Does this step have anything to animate?
export function hasMovement(diagram) {
  return diagram.actions.length > 0;
}

// Starts and stops gently instead of at a constant speed.
function ease(t) {
  const clamped = Math.min(1, Math.max(0, t));
  return clamped < 0.5 ? 2 * clamped * clamped : 1 - 2 * (1 - clamped) * (1 - clamped);
}
