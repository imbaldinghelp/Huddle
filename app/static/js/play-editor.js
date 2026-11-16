// The court editor (admins only): drag players, draw arrows, manage steps,
// undo, and save the play to the server as JSON.

import { createCourt, fromView, toView } from "./court/court.js";
import { distance, pathLength, simplify } from "./court/geometry.js";
import {
  addDefenders,
  findPlayer,
  giveBall,
  hasDefenders,
  nextDiagram,
  removeDefenders,
  startingDiagram,
} from "./court/model.js";
import { BALL_OFFSET, renderDiagram } from "./court/render.js";
import { pathData, svgElement } from "./court/svg.js";

// These limits match app/playbook/validation.py.
const MAX_STEPS = 20;
const MAX_PATH_POINTS = 12;
const MAX_UNDO = 30;
// Distances in drawing units (1 unit = 10 cm on a real court).
const SNAP_DISTANCE = 11; // how near a player a pass or the ball must be dropped
const MIN_ARROW_LENGTH = 7; // shorter drags are treated as an accidental click

const TOOL_HINTS = {
  move: "Drag a player to move them. Drag the ball onto a player to change who has it.",
  cut: "Drag from a player along the path of their cut.",
  dribble: "Drag from the player with the ball along the path of their dribble.",
  pass: "Drag from the player with the ball to a teammate.",
  screen: "Drag from a player to the spot where they set the screen.",
  erase: "Click an arrow to remove it.",
};
const SAVE_FAILED =
  "Huddle could not save the play. Check your connection and try again. " +
  "If you were logged out, log in from another tab first, then save here.";

const editor = document.querySelector("[data-play-editor]");
const savedSteps = JSON.parse(document.getElementById("play-data").textContent).steps;

const fields = {
  title: document.getElementById("play-title"),
  category: document.getElementById("play-category"),
  summary: document.getElementById("play-summary"),
  coaching_notes: document.getElementById("play-notes"),
};
const descriptionField = document.getElementById("step-description");
const descriptionLabel = editor.querySelector("[data-description-label]");
const hint = editor.querySelector("[data-hint]");
const stepList = editor.querySelector("[data-step-list]");
const addStepButton = editor.querySelector("[data-add-step]");
const undoButton = editor.querySelector("[data-undo]");
const defendersBox = editor.querySelector("[data-defenders]");
const saveButtons = [...editor.querySelectorAll("[data-save]")];
const saveErrors = editor.querySelector("[data-save-errors]");

const court = createCourt();
court.svg.setAttribute("role", "img");
court.svg.setAttribute("aria-label", "Court diagram. Use a mouse or touch to move players and draw arrows.");
editor.querySelector("[data-court]").append(court.svg);

// Everything the editor is working on. The page is redrawn from this.
const state = {
  steps: savedSteps.length > 0 ? savedSteps : [{ description: "", diagram: startingDiagram() }],
  current: 0,
  tool: "move",
};
// Earlier copies of the steps (as JSON text), newest last, for Undo.
const undoStack = [];
let unsaved = false;
// What the mouse is dragging right now, or null.
let drag = null;
// True while the step description is being typed, so one Undo covers the whole edit.
let typingDescription = false;

function currentStep() {
  return state.steps[state.current];
}

function currentDiagram() {
  return currentStep().diagram;
}

// ---------- Undo ----------

// Call this just before changing the steps.
function remember() {
  undoStack.push(JSON.stringify({ steps: state.steps, current: state.current }));
  if (undoStack.length > MAX_UNDO) {
    undoStack.shift();
  }
  unsaved = true;
}

function undo() {
  if (undoStack.length === 0) {
    return;
  }
  const previous = JSON.parse(undoStack.pop());
  state.steps = previous.steps;
  state.current = previous.current;
  render();
}

// ---------- Drawing the page from the state ----------

function render() {
  renderCourt();
  renderStepList();
  descriptionField.value = currentStep().description;
  descriptionLabel.textContent = `Step ${state.current + 1} description`;
  defendersBox.checked = hasDefenders(currentDiagram());
  undoButton.disabled = undoStack.length === 0;
  addStepButton.disabled = state.steps.length >= MAX_STEPS;
}

function renderCourt() {
  let diagram = currentDiagram();
  const options = {};

  if (drag?.kind === "ball") {
    options.ballAt = [drag.point[0] - BALL_OFFSET, drag.point[1] - BALL_OFFSET];
  }
  // While an arrow is being drawn, show it without changing the real diagram yet.
  const preview = drag?.kind === "draw" ? drawnMove(drag) : null;
  if (preview) {
    diagram = { ...diagram, actions: [...withoutMove(diagram.actions, preview.player), preview] };
  }

  renderDiagram(court.diagram, diagram, options);
  if (drag?.kind === "pass") {
    court.diagram.prepend(passPreview(drag));
  }
}

function passPreview(passDrag) {
  const passer = findPlayer(currentDiagram(), passDrag.playerId);
  const target = nearestTeammate(passDrag.point, passDrag.playerId);
  const end = target ? toView([target.x, target.y]) : passDrag.point;
  const line = svgElement("path", { class: "court-action-line", d: pathData([toView([passer.x, passer.y]), end]) });
  return svgElement("g", { class: "court-action court-action-pass" }, [line]);
}

function renderStepList() {
  const items = state.steps.map((step, index) => {
    const number = index + 1;
    const select = element("button", { class: "step-select", type: "button" }, [
      element("span", { class: "step-name" }, [`Step ${number}`]),
      element("span", { class: "step-preview" }, [step.description || "No description yet"]),
    ]);
    select.dataset.stepAction = "select";

    const up = stepButton("Up", `Move step ${number} up`, "up", index === 0);
    const down = stepButton("Down", `Move step ${number} down`, "down", index === state.steps.length - 1);
    const remove = stepButton("Remove", `Remove step ${number}`, "remove", state.steps.length === 1);

    const item = element("li", { class: "step-item" }, [select, element("div", { class: "step-actions" }, [up, down, remove])]);
    item.dataset.stepIndex = index;
    if (index === state.current) {
      item.setAttribute("aria-current", "step");
    }
    return item;
  });
  stepList.replaceChildren(...items);
}

function stepButton(text, label, action, disabled) {
  const button = element("button", { class: "text-button", type: "button", "aria-label": label }, [text]);
  button.dataset.stepAction = action;
  button.disabled = disabled;
  return button;
}

// Builds an HTML element: element("p", { class: "note" }, ["Hello"]).
function element(tag, attributes = {}, children = []) {
  const node = document.createElement(tag);
  for (const [name, value] of Object.entries(attributes)) {
    node.setAttribute(name, value);
  }
  node.append(...children);
  return node;
}

function showHint(message) {
  hint.textContent = message;
}

// ---------- Tools ----------

function chooseTool(tool) {
  state.tool = tool;
  // The CSS uses data-tool to pick the right mouse cursor.
  court.svg.dataset.tool = tool;
  for (const button of editor.querySelectorAll("[data-tool]")) {
    button.setAttribute("aria-pressed", String(button.dataset.tool === tool));
  }
  showHint(TOOL_HINTS[tool]);
}

// ---------- Mouse and touch on the court ----------

// Where the pointer is, in drawing units.
function pointerPosition(event) {
  const toDrawing = court.svg.getScreenCTM().inverse();
  const point = new DOMPoint(event.clientX, event.clientY).matrixTransform(toDrawing);
  return [point.x, point.y];
}

function onPointerDown(event) {
  const hit = event.target.closest("[data-player-id], [data-ball], [data-action-index]");
  if (!hit || event.button !== 0) {
    return;
  }
  const diagram = currentDiagram();

  if (state.tool === "erase") {
    if (hit.dataset.actionIndex !== undefined) {
      remember();
      diagram.actions.splice(Number(hit.dataset.actionIndex), 1);
      render();
    }
    return;
  }

  const onBall = hit.hasAttribute("data-ball");
  const playerId = onBall ? diagram.ball.holder : hit.dataset.playerId;
  if (!playerId) {
    return;
  }
  const point = pointerPosition(event);

  if (state.tool === "move") {
    drag = { kind: onBall ? "ball" : "player", playerId, point, moved: false };
  } else if ((state.tool === "pass" || state.tool === "dribble") && playerId !== diagram.ball.holder) {
    showHint(`Only the player with the ball can ${state.tool}. Start from player ${diagram.ball.holder.slice(1)}.`);
    return;
  } else if (state.tool === "pass") {
    drag = { kind: "pass", playerId, point };
  } else {
    drag = { kind: "draw", tool: state.tool, playerId, points: [point] };
  }
  // Keep receiving this pointer's events even if it leaves the court.
  court.svg.setPointerCapture(event.pointerId);
  event.preventDefault();
}

function onPointerMove(event) {
  if (!drag) {
    return;
  }
  const point = pointerPosition(event);
  drag.point = point;

  if (drag.kind === "player") {
    if (!drag.moved) {
      remember();
      drag.moved = true;
    }
    const player = findPlayer(currentDiagram(), drag.playerId);
    [player.x, player.y] = fromView(point);
  } else if (drag.kind === "draw" && distance(point, drag.points[drag.points.length - 1]) > 1) {
    drag.points.push(point);
  }
  renderCourt();
}

function onPointerUp() {
  if (!drag) {
    return;
  }
  const finished = drag;
  drag = null;
  const diagram = currentDiagram();

  if (finished.kind === "ball") {
    const target = nearestTeammate(finished.point, null);
    if (target && target.id !== diagram.ball.holder) {
      remember();
      giveBall(diagram, target.id);
    }
  } else if (finished.kind === "pass") {
    const target = nearestTeammate(finished.point, finished.playerId);
    if (target) {
      remember();
      diagram.actions = diagram.actions.filter((action) => action.type !== "pass");
      diagram.actions.push({ type: "pass", from: finished.playerId, to: target.id });
    } else {
      showHint("Drop the pass on a teammate (players 1 to 5).");
    }
  } else if (finished.kind === "draw") {
    const move = drawnMove(finished);
    if (move) {
      remember();
      diagram.actions = [...withoutMove(diagram.actions, move.player), move];
    }
  }
  render();
}

// Turns a mouse drag into a cut, dribble or screen. Returns null for a drag
// too short to be meant.
function drawnMove(drawDrag) {
  if (pathLength(drawDrag.points) < MIN_ARROW_LENGTH) {
    return null;
  }
  // Loosen the tolerance until few enough points are left to save.
  let tolerance = 2.5;
  let points = simplify(drawDrag.points, tolerance);
  while (points.length > MAX_PATH_POINTS + 1) {
    tolerance *= 1.5;
    points = simplify(drawDrag.points, tolerance);
  }
  // The first point is where the drag began: on the player, who is the start already.
  return { type: drawDrag.tool, player: drawDrag.playerId, path: points.slice(1).map(fromView) };
}

// A player has one move per step, so a new one replaces the old one.
function withoutMove(actions, playerId) {
  return actions.filter((action) => action.type === "pass" || action.player !== playerId);
}

// The attacker closest to a point, if one is near enough to count as "on" it.
function nearestTeammate(point, excludedId) {
  let nearest = null;
  let nearestDistance = SNAP_DISTANCE;
  for (const player of currentDiagram().players) {
    const gap = distance(point, toView([player.x, player.y]));
    if (player.team === "offense" && player.id !== excludedId && gap < nearestDistance) {
      nearest = player;
      nearestDistance = gap;
    }
  }
  return nearest;
}

// ---------- Steps ----------

function addStep() {
  if (state.steps.length >= MAX_STEPS) {
    return;
  }
  remember();
  const newStep = { description: "", diagram: nextDiagram(currentDiagram()) };
  state.steps.splice(state.current + 1, 0, newStep);
  state.current += 1;
  render();
  descriptionField.focus();
}

function onStepListClick(event) {
  const button = event.target.closest("[data-step-action]");
  if (!button) {
    return;
  }
  const action = button.dataset.stepAction;
  const index = Number(button.closest("[data-step-index]").dataset.stepIndex);
  let focusIndex = index;

  if (action === "select") {
    state.current = index;
  } else if (action === "remove") {
    remember();
    state.steps.splice(index, 1);
    state.current = Math.min(state.current, state.steps.length - 1);
    focusIndex = Math.min(index, state.steps.length - 1);
  } else {
    const swapWith = action === "up" ? index - 1 : index + 1;
    remember();
    [state.steps[index], state.steps[swapWith]] = [state.steps[swapWith], state.steps[index]];
    state.current = swapWith;
    focusIndex = swapWith;
  }
  render();
  focusStepButton(focusIndex, action);
}

// The list is rebuilt on every change, so put keyboard focus back where it was.
function focusStepButton(index, action) {
  const item = stepList.children[index];
  const button = item.querySelector(`[data-step-action="${action}"]`);
  (button.disabled ? item.querySelector(".step-select") : button).focus();
}

function onDescriptionInput() {
  if (!typingDescription) {
    remember();
    typingDescription = true;
    undoButton.disabled = false;
  }
  currentStep().description = descriptionField.value;
  renderStepList();
}

function toggleDefenders() {
  remember();
  for (const step of state.steps) {
    if (defendersBox.checked) {
      addDefenders(step.diagram);
    } else {
      removeDefenders(step.diagram);
    }
  }
  render();
}

// ---------- Saving ----------

async function save(status) {
  setSaving(true);
  const payload = {
    title: fields.title.value,
    category: fields.category.value,
    summary: fields.summary.value,
    coaching_notes: fields.coaching_notes.value,
    status,
    steps: state.steps,
  };

  let result = null;
  try {
    const response = await fetch(editor.dataset.saveUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": editor.dataset.csrfToken },
      body: JSON.stringify(payload),
    });
    result = await response.json();
  } catch {
    // No connection, or the server answered with a page instead of JSON.
  }

  if (result?.redirect) {
    unsaved = false;
    window.location.assign(result.redirect);
    return;
  }
  showSaveErrors(result?.errors ?? [SAVE_FAILED]);
  setSaving(false);
}

function setSaving(saving) {
  for (const button of saveButtons) {
    button.disabled = saving;
  }
  if (saving) {
    saveErrors.replaceChildren();
  }
}

function showSaveErrors(messages) {
  saveErrors.replaceChildren(...messages.map((message) => element("p", { class: "form-message" }, [message])));
  saveErrors.scrollIntoView({ block: "nearest" });
}

// ---------- Wiring it all up ----------

court.svg.addEventListener("pointerdown", onPointerDown);
court.svg.addEventListener("pointermove", onPointerMove);
court.svg.addEventListener("pointerup", onPointerUp);
court.svg.addEventListener("pointercancel", onPointerUp);

for (const button of editor.querySelectorAll("[data-tool]")) {
  button.addEventListener("click", () => chooseTool(button.dataset.tool));
}
undoButton.addEventListener("click", undo);
defendersBox.addEventListener("change", toggleDefenders);
addStepButton.addEventListener("click", addStep);
stepList.addEventListener("click", onStepListClick);
descriptionField.addEventListener("input", onDescriptionInput);
descriptionField.addEventListener("blur", () => (typingDescription = false));

for (const field of Object.values(fields)) {
  field.addEventListener("input", () => (unsaved = true));
}
for (const button of saveButtons) {
  button.addEventListener("click", () => save(button.dataset.save));
}

// Ctrl+Z (Cmd+Z on a Mac) undoes court changes, but not while typing in a
// text box, where the browser's own undo should handle the text.
document.addEventListener("keydown", (event) => {
  const typing = event.target.matches("input, textarea, select");
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "z" && !typing) {
    event.preventDefault();
    undo();
  }
});

// Ask before leaving the page with changes that have not been saved.
window.addEventListener("beforeunload", (event) => {
  if (unsaved) {
    event.preventDefault();
  }
});

chooseTool("move");
render();
