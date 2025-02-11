// ----- CLASS DEFINITIONS -----

class Car {
    constructor(progress, speed, roadId, lane) {
      this.progress = progress;
      this.speed = speed;
      this.roadId = roadId;
      this.lane = lane;
      
      // Bigger cars
      this.length = 50;
      this.width = 25;
      
      // Random color to make each car distinct.
      const colors = ['#ffcc00', '#1abc9c', '#3498db', '#e67e22', '#9b59b6'];
      this.color = colors[Math.floor(Math.random() * colors.length)];
    }
  }
  
  class Lane {
    constructor(roadId, offset) {
      this.cars = [];
      this.roadId = roadId;
      this.offset = offset;
    }
  }
  
  class Road {
    constructor(id, start, end) {
      this.id = id;
      this.start = start;
      this.end = end;
      this.laneCount = 3;
      this.lanes = [];
      
      // More spacing between lanes
      const laneOffsets = [-35, 0, 35];
      for (let offset of laneOffsets) {
        this.lanes.push(new Lane(this.id, offset));
      }
      
      // For drawing/position calculations:
      this.angle = Math.atan2(end.y - start.y, end.x - start.x);
      const dx = end.x - start.x;
      const dy = end.y - start.y;
      const mag = Math.sqrt(dx * dx + dy * dy);
      this.dir = { x: dx / mag, y: dy / mag };
      this.perp = { x: -this.dir.y, y: this.dir.x };
    }
  }
  
  class TrafficLight {
    constructor(origins, state) {
      this.origins = origins;
      this.state = state;
    }
  }
  
  // Expose these classes for use elsewhere if needed
  window.Car = Car;
  window.Lane = Lane;
  window.Road = Road;
  window.TrafficLight = TrafficLight;
  