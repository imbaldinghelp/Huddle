// Draws the court lines. This is the only file that knows the court's shape,
// so a full court can be added later by drawing a second set of lines here.

import { svgElement } from "./svg.js";

// Sizes are in decimetres (10 = 1 metre) and follow the FIBA court.
const COURT_WIDTH = 150;
const HALF_LENGTH = 140;
// Space around the lines, so an inbounder can stand out of bounds.
const MARGIN = 10;
const BASKET_FROM_BASELINE = 15.75;
const THREE_POINT_RADIUS = 67.5;
const KEY_WIDTH = 49;
const KEY_LENGTH = 58;

// The whole drawing: the half court plus its margin. The baseline is at the top.
export const VIEW = { width: COURT_WIDTH + MARGIN * 2, height: HALF_LENGTH + MARGIN * 2 };
export const BASKET = [MARGIN + COURT_WIDTH / 2, MARGIN + BASKET_FROM_BASELINE];

// Saved positions are fractions from 0 to 1 so they fit any screen size.
// toView turns one into drawing units; fromView goes back the other way.
export function toView([x, y]) {
  return [x * VIEW.width, y * VIEW.height];
}

export function fromView([x, y]) {
  return [clampFraction(x / VIEW.width), clampFraction(y / VIEW.height)];
}

function clampFraction(value) {
  return Math.round(Math.min(1, Math.max(0, value)) * 10000) / 10000;
}

// Builds the <svg>. Returns it with the empty layer that players and arrows
// are drawn into (see render.js).
export function createCourt() {
  const lines = svgElement("g", { class: "court-lines", transform: `translate(${MARGIN} ${MARGIN})` }, courtLines());
  const diagram = svgElement("g", { class: "court-diagram" });
  const svg = svgElement("svg", { class: "court", viewBox: `0 0 ${VIEW.width} ${VIEW.height}` }, [lines, diagram]);
  return { svg, diagram };
}

function courtLines() {
  const middle = COURT_WIDTH / 2;
  const keyLeft = middle - KEY_WIDTH / 2;
  // The three-point line runs straight up from the baseline, 9 dm inside each
  // sideline, until it meets the arc around the basket.
  const cornerInset = 9;
  const arcStartY = BASKET_FROM_BASELINE + Math.sqrt(THREE_POINT_RADIUS ** 2 - (middle - cornerInset) ** 2);

  return [
    svgElement("rect", { class: "court-key", x: keyLeft, y: 0, width: KEY_WIDTH, height: KEY_LENGTH }),
    // Free-throw circle (the half outside the key) and the centre circle.
    svgElement("path", { d: `M ${middle - 18} ${KEY_LENGTH} A 18 18 0 0 0 ${middle + 18} ${KEY_LENGTH}` }),
    svgElement("path", { d: `M ${middle - 18} ${HALF_LENGTH} A 18 18 0 0 1 ${middle + 18} ${HALF_LENGTH}` }),
    svgElement("path", {
      d:
        `M ${cornerInset} 0 V ${arcStartY} ` +
        `A ${THREE_POINT_RADIUS} ${THREE_POINT_RADIUS} 0 0 0 ${COURT_WIDTH - cornerInset} ${arcStartY} V 0`,
    }),
    // No-charge semicircle, backboard and rim.
    svgElement("path", {
      d: `M ${middle - 12.5} ${BASKET_FROM_BASELINE} A 12.5 12.5 0 0 0 ${middle + 12.5} ${BASKET_FROM_BASELINE}`,
    }),
    svgElement("path", { class: "court-backboard", d: `M ${middle - 9} 12 H ${middle + 9}` }),
    svgElement("circle", { cx: middle, cy: BASKET_FROM_BASELINE, r: 2.25 }),
    // Baseline, sidelines and the half-court line.
    svgElement("rect", { class: "court-boundary", x: 0, y: 0, width: COURT_WIDTH, height: HALF_LENGTH }),
  ];
}
