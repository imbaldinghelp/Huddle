// Maths for lines on the court. A point is [x, y]; a path is a list of points.
// Nothing here touches the page, so every function is easy to test on its own.

export function distance(a, b) {
  return Math.hypot(b[0] - a[0], b[1] - a[1]);
}

// The point part of the way from a to b: t = 0 is a, t = 1 is b.
export function lerp(a, b, t) {
  return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
}

export function pathLength(points) {
  let total = 0;
  for (let i = 0; i < points.length - 1; i++) {
    total += distance(points[i], points[i + 1]);
  }
  return total;
}

// The part of a path between two distances measured from its start.
// Used to stop a line short of a player marker or an arrowhead.
export function slicePath(points, start, end) {
  const result = [];
  let walked = 0;
  for (let i = 0; i < points.length - 1; i++) {
    const length = distance(points[i], points[i + 1]);
    const from = Math.max(start, walked);
    const to = Math.min(end, walked + length);
    if (length > 0 && from < to) {
      if (result.length === 0) {
        result.push(lerp(points[i], points[i + 1], (from - walked) / length));
      }
      result.push(lerp(points[i], points[i + 1], (to - walked) / length));
    }
    walked += length;
  }
  return result;
}

// The point a fraction of the way along a path: 0 is the start, 1 the end.
export function pointAlong(points, fraction) {
  const target = pathLength(points) * fraction;
  let walked = 0;
  for (let i = 0; i < points.length - 1; i++) {
    const length = distance(points[i], points[i + 1]);
    if (length > 0 && walked + length >= target) {
      return lerp(points[i], points[i + 1], (target - walked) / length);
    }
    walked += length;
  }
  return points[points.length - 1];
}

// Which way a path is heading when it ends, as a step of length 1.
export function endDirection(points) {
  for (let i = points.length - 1; i > 0; i--) {
    const length = distance(points[i - 1], points[i]);
    if (length > 0.001) {
      return [(points[i][0] - points[i - 1][0]) / length, (points[i][1] - points[i - 1][1]) / length];
    }
  }
  return [0, -1];
}

// Rounds the corners of a path by adding points along a curve that passes
// through every original point (a Catmull-Rom spline).
export function smooth(points, pointsPerSection = 8) {
  if (points.length < 3) {
    return points;
  }
  const result = [points[0]];
  for (let i = 0; i < points.length - 1; i++) {
    const before = points[Math.max(i - 1, 0)];
    const after = points[Math.min(i + 2, points.length - 1)];
    for (let step = 1; step <= pointsPerSection; step++) {
      const t = step / pointsPerSection;
      result.push([
        curveValue(before[0], points[i][0], points[i + 1][0], after[0], t),
        curveValue(before[1], points[i][1], points[i + 1][1], after[1], t),
      ]);
    }
  }
  return result;
}

// One coordinate of the curve between b and c; a and d are the neighbours that bend it.
function curveValue(a, b, c, d, t) {
  return 0.5 * (2 * b + (c - a) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (3 * b - a - 3 * c + d) * t * t * t);
}

// A zigzag that follows a path, stepping from side to side. Used for dribbles.
export function zigzag(points, amplitude, stepLength) {
  const steps = Math.max(2, Math.round(pathLength(points) / stepLength));
  const result = [points[0]];
  for (let i = 1; i < steps; i++) {
    const fraction = i / steps;
    const centre = pointAlong(points, fraction);
    const [dx, dy] = endDirection([pointAlong(points, fraction - 0.01), pointAlong(points, fraction + 0.01)]);
    const side = i % 2 === 0 ? amplitude : -amplitude;
    // (-dy, dx) points sideways from the direction of travel.
    result.push([centre[0] - dy * side, centre[1] + dx * side]);
  }
  result.push(points[points.length - 1]);
  return result;
}

// Removes points that barely change a path's shape, so a wobbly mouse drag
// becomes a few clean points (the Ramer-Douglas-Peucker method).
export function simplify(points, tolerance) {
  if (points.length < 3) {
    return points;
  }
  const first = points[0];
  const last = points[points.length - 1];
  let furthest = 0;
  let furthestIndex = 0;
  for (let i = 1; i < points.length - 1; i++) {
    const gap = distanceToLine(points[i], first, last);
    if (gap > furthest) {
      furthest = gap;
      furthestIndex = i;
    }
  }
  if (furthest <= tolerance) {
    return [first, last];
  }
  // Keep the point that sticks out most and simplify each side of it.
  const left = simplify(points.slice(0, furthestIndex + 1), tolerance);
  const right = simplify(points.slice(furthestIndex), tolerance);
  return [...left.slice(0, -1), ...right];
}

// How far a point is from the straight line between a and b.
function distanceToLine(point, a, b) {
  const length = distance(a, b);
  if (length === 0) {
    return distance(point, a);
  }
  const along = ((point[0] - a[0]) * (b[0] - a[0]) + (point[1] - a[1]) * (b[1] - a[1])) / (length * length);
  return distance(point, lerp(a, b, Math.min(1, Math.max(0, along))));
}
