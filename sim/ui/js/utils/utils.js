// js/utils/utils.js
/**
 * Draw a rounded rectangle.
 * @param {Phaser.GameObjects.Graphics} graphics
 * @param {number} x
 * @param {number} y
 * @param {number} width
 * @param {number} height
 * @param {number} radius
 */
export function roundRect(graphics, x, y, width, height, radius) {
  graphics.fillRoundedRect(x, y, width, height, radius);
}

/**
 * Euclidean distance between two points.
 * @param {Object} a
 * @param {Object} b
 * @returns {number}
 */
export function distance(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

/**
 * Convert a pixel distance to a progress fraction along the road.
 * @param {Road} road
 * @param {number} pixels
 * @returns {number}
 */
export function pixelsToProgress(road, pixels) {
  return pixels / roadLength(road);
}

/**
 * Compute the length of the road (in pixels).
 * @param {Road} road
 * @returns {number}
 */
export function roadLength(road) {
  const dx = road.end.x - road.start.x;
  const dy = road.end.y - road.start.y;
  return Math.hypot(dx, dy);
}

/**
 * Compute the distance (in pixels) from a car’s current position to the road’s stop line.
 * @param {Car} car
 * @param {Road} road
 * @returns {number}
 */
export function distanceToStopLine(car, road) {
  const roadLen = roadLength(road);
  const carPx = car.positionProgress * roadLen;
  const stopPx = road.stopProgress * roadLen;
  return Math.max(0, stopPx - carPx);
}

/**
 * Compute the gap (in pixels) between two cars along the road.
 * @param {Car} car
 * @param {Car} frontCar
 * @param {Road} road
 * @returns {number}
 */
export function distanceBetweenCars(car, frontCar, road) {
  const roadLen = roadLength(road);
  const carPx = car.positionProgress * roadLen;
  const frontCarPx = frontCar.positionProgress * roadLen;
  return Math.max(0, frontCarPx - carPx);
}

/**
 * Given a road’s start/end points and the intersection bounds,
 * compute the normalized progress (t value) at which the road “hits” the intersection.
 * @param {Object} start
 * @param {Object} end
 * @param {number} left
 * @param {number} right
 * @param {number} top
 * @param {number} bottom
 * @returns {number}
 */
export function computeStopProgress(start, end, left, right, top, bottom) {
  const sx = start.x, sy = start.y;
  const ex = end.x, ey = end.y;
  const tValues = [];

  function intersectX(xLine) {
    const dx = ex - sx;
    if (Math.abs(dx) < 1e-9) return;
    const t = (xLine - sx) / dx;
    if (t >= 0 && t <= 1) {
      const yHit = sy + t * (ey - sy);
      if (yHit >= top && yHit <= bottom) tValues.push(t);
    }
  }
  function intersectY(yLine) {
    const dy = ey - sy;
    if (Math.abs(dy) < 1e-9) return;
    const t = (yLine - sy) / dy;
    if (t >= 0 && t <= 1) {
      const xHit = sx + t * (ex - sx);
      if (xHit >= left && xHit <= right) tValues.push(t);
    }
  }
  intersectX(left);
  intersectX(right);
  intersectY(top);
  intersectY(bottom);
  return tValues.length === 0 ? 1 : Math.min(...tValues);
}
