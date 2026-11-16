// The play page: shows one step at a time, with Previous/Next buttons,
// the left and right arrow keys, and a Play button that animates the moves.

import { frameAt, hasMovement } from "./court/animate.js";
import { createCourt } from "./court/court.js";
import { renderDiagram } from "./court/render.js";

const HOLD_TIME = 900; // ms a step is shown still before it starts to move
const MOVE_TIME = 1600; // ms the players take to run a step

const viewer = document.querySelector("[data-play-viewer]");
const steps = JSON.parse(document.getElementById("play-data").textContent).steps;
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

const previousButton = viewer.querySelector("[data-previous]");
const nextButton = viewer.querySelector("[data-next]");
const playButton = viewer.querySelector("[data-play]");
const stepCount = viewer.querySelector("[data-step-count]");
const stepDescription = viewer.querySelector("[data-step-description]");
const stepTrack = viewer.querySelector("[data-step-track]");

const court = createCourt();
court.svg.setAttribute("role", "img");
viewer.querySelector("[data-court]").append(court.svg);

let current = 0;
// Each press of Play starts a numbered run. Stopping (or starting again)
// changes the number, and the old run notices and gives up.
let playRun = 0;
let playing = false;

// ---------- Showing a step ----------

function showStep(index) {
  current = index;
  const step = steps[current];
  renderDiagram(court.diagram, step.diagram);
  court.svg.setAttribute("aria-label", `Court diagram, step ${current + 1} of ${steps.length}`);

  stepCount.textContent = `Step ${current + 1} of ${steps.length}`;
  stepDescription.textContent = step.description || "No notes for this step.";
  stepDescription.classList.toggle("is-empty", !step.description);

  // aria-disabled (not disabled) keeps keyboard focus on the button at either end.
  previousButton.setAttribute("aria-disabled", String(current === 0));
  nextButton.setAttribute("aria-disabled", String(current === steps.length - 1));
  [...stepTrack.children].forEach((mark, markIndex) => {
    mark.classList.toggle("is-current", markIndex === current);
  });
}

function goTo(index) {
  if (index < 0 || index >= steps.length) {
    return;
  }
  stopPlaying();
  showStep(index);
}

// ---------- Playing the whole play ----------

async function startPlaying() {
  const run = ++playRun;
  playing = true;
  playButton.textContent = "Stop";
  if (current === steps.length - 1) {
    showStep(0);
  }

  while (true) {
    await wait(HOLD_TIME);
    if (run !== playRun) {
      return;
    }
    await animateStep(steps[current].diagram, run);
    if (run !== playRun) {
      return;
    }
    if (current === steps.length - 1) {
      break;
    }
    showStep(current + 1);
  }

  // Hold the final picture for a moment, then put the last step back.
  await wait(HOLD_TIME);
  if (run === playRun) {
    stopPlaying();
  }
}

function stopPlaying() {
  if (!playing) {
    return;
  }
  playRun++;
  playing = false;
  playButton.textContent = "Play";
  showStep(current);
}

function animateStep(diagram, run) {
  // With reduced motion switched on, steps change without anything sliding.
  if (!hasMovement(diagram) || reducedMotion.matches) {
    return wait(HOLD_TIME);
  }
  return new Promise((resolve) => {
    const startedAt = performance.now();
    function drawFrame(now) {
      if (run !== playRun) {
        resolve();
        return;
      }
      const progress = Math.min(1, (now - startedAt) / MOVE_TIME);
      renderDiagram(court.diagram, diagram, frameAt(diagram, progress));
      if (progress < 1) {
        requestAnimationFrame(drawFrame);
      } else {
        resolve();
      }
    }
    requestAnimationFrame(drawFrame);
  });
}

function wait(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

// ---------- Buttons and keys ----------

previousButton.addEventListener("click", () => goTo(current - 1));
nextButton.addEventListener("click", () => goTo(current + 1));
playButton.addEventListener("click", () => (playing ? stopPlaying() : startPlaying()));

document.addEventListener("keydown", (event) => {
  if (event.altKey || event.ctrlKey || event.metaKey) {
    return;
  }
  if (event.key === "ArrowLeft") {
    goTo(current - 1);
  } else if (event.key === "ArrowRight") {
    goTo(current + 1);
  }
});

// A play with a single still picture has nothing to step through or animate.
const somethingMoves = steps.some((step) => hasMovement(step.diagram));
viewer.querySelector("[data-step-controls]").hidden = steps.length === 1 && !somethingMoves;
previousButton.hidden = nextButton.hidden = steps.length === 1;

for (let i = 0; i < steps.length; i++) {
  stepTrack.append(document.createElement("span"));
}
stepTrack.hidden = steps.length === 1;

showStep(0);
