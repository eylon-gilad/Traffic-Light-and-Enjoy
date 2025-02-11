/**************************************
 *  classes.js
 **************************************/

class Car {
  /**
   * @param {number} progress 0..1 along the road
   * @param {number} speed Rate of progress change per frame
   * @param {string} roadId e.g. 'east1', 'west2', etc.
   * @param {Lane} lane The Lane object
   */
  constructor(progress, speed, roadId, lane) {
    this.progress = progress;
    this.speed = speed;
    this.roadId = roadId;
    this.lane = lane;

    // Car dimensions
    this.length = 50;
    this.width = 25;

    // Random color for variety
    const colors = ['#ffcc00', '#1abc9c', '#3498db', '#e67e22', '#9b59b6', '#663399'];
    this.color = colors[Math.floor(Math.random() * colors.length)];
  }
}

class Lane {
  constructor(roadId, offset) {
    this.roadId = roadId;
    this.offset = offset;
    this.cars = [];
  }
}

class Road {
  /**
   * @param {string} id e.g. 'east1', 'west2'
   * @param {{x:number, y:number}} start
   * @param {{x:number, y:number}} end
   */
  constructor(id, start, end) {
    this.id = id;
    this.start = start;
    this.end = end;
    this.laneCount = 3;
    this.lanes = [];

    // Lane offsets
    const laneOffsets = [-35, 0, 35];
    laneOffsets.forEach(offset => {
      this.lanes.push(new Lane(this.id, offset));
    });

    // Compute direction vectors
    this.angle = Math.atan2(end.y - start.y, end.x - start.x);
    const dx = end.x - start.x;
    const dy = end.y - start.y;
    const mag = Math.sqrt(dx*dx + dy*dy);
    this.dir  = { x: dx/mag, y: dy/mag };
    this.perp = { x: -this.dir.y, y: this.dir.x };
  }
}

class TrafficLight {
  /**
   * @param {string[]} origins Array of Road IDs e.g. ['east1','west1']
   * @param {boolean} state true=green, false=red
   */
  constructor(origins, state) {
    this.origins = origins;
    this.state = state;
  }
}

// Expose classes to global scope
window.Car = Car;
window.Lane = Lane;
window.Road = Road;
window.TrafficLight = TrafficLight;