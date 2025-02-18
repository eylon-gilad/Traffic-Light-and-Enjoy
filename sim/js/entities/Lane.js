// js/entities/Lane.js
/**
 * Represents a single lane on a road.
 */
export default class Lane {
  /**
   * @param {string} roadId - The ID of the road (e.g. "TLE-R1").
   * @param {number} offset - Lateral offset from the center of the road.
   * @param {number} index - The lane’s index (0 = left–most).
   */
  constructor(roadId, offset, index) {
    this.roadId = roadId;
    this.offset = offset;
    this.index = index;
    this.cars = [];
    // Assign an ID in the format "TLE-R{n}-L{m+1}"
    this.id = `${roadId}-L${index + 1}`;
    // The parent Road will assign this.road later.
    this.road = null;
    // Initialize a counter for the next car in this lane.
    this.nextCarId = 1;
    // The destination lanes for this lane.
    this.destinationLanes = [this];
  }
}
