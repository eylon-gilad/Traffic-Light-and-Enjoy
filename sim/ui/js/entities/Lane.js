// js/entities/Lane.js
/**
 * Represents a single lane on a road.
 */
export default class Lane {
  /**
   * @param {string} roadId - The identifier of the road.
   * @param {number} offset - Lateral offset from the center of the road.
   */
  constructor(roadId, offset) {
    this.roadId = roadId;
    this.offset = offset;
    this.cars = [];
    // This will be set by the Road upon creation.
    this.road = null;
  }
}
