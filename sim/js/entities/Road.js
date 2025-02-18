// js/entities/Road.js
import Lane from "./Lane.js";

/**
 * Represents a road that spans from one point to another.
 */
export default class Road {
  // Static counter for roads.
  static nextRoadId = 1;

  /**
   * @param {Object} start - Start point {x, y}.
   * @param {Object} end - End point {x, y}.
   * @param {number} laneCount - How many lanes the road has.
   * @param {number} roadWidth - The width of the road (in pixels).
   */
  constructor(start, end, laneCount = 3, roadWidth = 100) {
    this._roadNumber = Road.nextRoadId++;
    this.id = `TLE-R${this._roadNumber}`;

    this.start = start;
    this.end = end;
    this.laneCount = laneCount;
    this.roadWidth = roadWidth;
    this.lanes = [];

    // Create lane objects with symmetric offsets.
    for (let i = 0; i < laneCount; i++) {
      const offset = (i - (laneCount - 1) / 2) * (roadWidth / laneCount);
      // Pass this road's id and the lane index.
      const lane = new Lane(this.id, offset, i);
      lane.road = this;
      this.lanes.push(lane);
    }

    // Precompute road geometry.
    const dx = end.x - start.x;
    const dy = end.y - start.y;
    const magnitude = Math.hypot(dx, dy);
    this.angle = Math.atan2(dy, dx);
    this.dir = { x: dx / magnitude, y: dy / magnitude };
    this.perp = { x: -this.dir.y, y: this.dir.x };

    // Default stop progress (can be updated later).
    this.stopProgress = 0.5;

    // Cache center for rendering.
    if (this.isVertical()) {
      this.cachedCenterX = start.x;
    } else {
      this.cachedCenterY = start.y;
    }
  }

  isVertical() {
    return (
      this.id.includes("R1") || this.id.includes("R2") || // if your roads are North/South
      Math.abs(this.start.x - this.end.x) < Math.abs(this.start.y - this.end.y)
    );
  }
}
