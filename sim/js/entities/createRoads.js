// js/entities/createRoads.js
import Road from "./Road.js";
import { computeStopProgress } from "../utils/utils.js";

/**
 * Create an array of four roads (north, south, east, and west) with three lanes each.
 * @param {number} centerX - Canvas center x–coordinate.
 * @param {number} centerY - Canvas center y–coordinate.
 * @param {number} canvasWidth - Canvas width.
 * @param {number} canvasHeight - Canvas height.
 * @param {number} roadWidth - Road width in pixels.
 * @returns {Array<Road>}
 */
export function createRoads(centerX, centerY, canvasWidth, canvasHeight, roadWidth) {
  const roads = [];
  // Define an intersection box.
  const left = centerX - roadWidth;
  const right = centerX + roadWidth;
  const top = centerY - roadWidth;
  const bottom = centerY + roadWidth;

  // Create four roads with start and end points outside the visible area.
  roads.push(new Road("north", { x: centerX - 100, y: -100 }, { x: centerX - 100, y: canvasHeight + 100 }, 3, roadWidth));
  roads.push(new Road("south", { x: centerX + 100, y: canvasHeight + 100 }, { x: centerX + 100, y: -100 }, 3, roadWidth));
  roads.push(new Road("east",  { x: -100, y: centerY + 100 }, { x: canvasWidth + 100, y: centerY + 100 }, 3, roadWidth));
  roads.push(new Road("west",  { x: canvasWidth + 100, y: centerY - 100 }, { x: -100, y: centerY - 100 }, 3, roadWidth));

  // Compute the stop progress for each road (where cars should stop at a red light).
  roads.forEach((road) => {
    road.centerX = centerX;
    road.centerY = centerY;
    const t = computeStopProgress(road.start, road.end, left, right, top, bottom);
    road.stopProgress = t;
  });
  return roads;
}
