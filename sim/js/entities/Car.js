// js/entities/Car.js
/**
 * Represents a car entity.
 */
export default class Car {
  /**
   * @param {number} positionProgress - Normalized position along the road (0 = start, 1 = end)
   * @param {number} baseSpeed - Base (normalized) speed for the car.
   * @param {Lane} lane - The lane that this car is on.
   */
  constructor(positionProgress, baseSpeed, lane) {
    this.positionProgress = positionProgress; // normalized position along the road
    // Initial speed: start at half the base speed.
    this.speed = baseSpeed * 0.5;
    // Desired (normalized) speed.
    this.desiredSpeed = baseSpeed;
    this.lane = lane;
    this.hasTurned = false;
    // For drawing purposes:
    this.currentLaneOffset = lane.offset;
    this.changingLane = false;
    this.length = 50;
    this.width = 25;
    this.color = "#ffcc00";
    // Reference to the sprite (for pooling in the Renderer).
    this.__sprite = null;

    // Use the lane's nextCarId counter to assign a unique car ID.
    this.id = `${lane.id}-C${lane.nextCarId++}`;
  }
}
