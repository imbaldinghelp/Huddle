// Helpers for building SVG elements from JavaScript.

const SVG_NAMESPACE = "http://www.w3.org/2000/svg";

// svgElement("circle", { r: 6 }) makes <circle r="6">.
export function svgElement(name, attributes = {}, children = []) {
  const element = document.createElementNS(SVG_NAMESPACE, name);
  for (const [key, value] of Object.entries(attributes)) {
    element.setAttribute(key, value);
  }
  element.append(...children);
  return element;
}

// Turns [[10, 20], [30, 40]] into the path text "M 10 20 L 30 40".
export function pathData(points) {
  return points
    .map(([x, y], index) => `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`)
    .join(" ");
}
