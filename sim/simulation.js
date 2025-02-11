// Grab our canvas and context
const canvas = document.getElementById('simulation');
const ctx = canvas.getContext('2d');

// Configure canvas size
canvas.width = 1600;
canvas.height = 1000;

// ----- SETUP ROADS & TRAFFIC LIGHT -----

// We'll place two horizontal roads: one for eastbound, one for westbound,
// with a gap of 60px between them.
const eastRoadCenterY = canvas.height / 2 - 60;
const westRoadCenterY = canvas.height / 2 + 60;

const roads = [];

// Road for eastbound traffic, left -> right
roads.push(new Road(
  'east',
  { x: -50, y: eastRoadCenterY },
  { x: canvas.width + 50, y: eastRoadCenterY }
));

// Road for westbound traffic, right -> left
roads.push(new Road(
  'west',
  { x: canvas.width + 50, y: westRoadCenterY },
  { x: -50, y: westRoadCenterY }
));

// One traffic light controlling both roads. We toggle every 2.5s here.
const ewLight = new TrafficLight(['east', 'west'], true);
setInterval(() => {
  ewLight.state = !ewLight.state;
}, 2500);

// The “stop line” is at progress = 0.45
const stopLine = 0.45;
// Cars maintain a certain gap to avoid overlapping
const safeGap = 0.05;

// ----- CAR SPAWNING -----
function spawnCar(road) {
  // Randomly pick one of the road's lanes
  const lane = road.lanes[Math.floor(Math.random() * road.lanes.length)];
  // Random speed between ~0.003 and 0.006
  const speed = Math.random() * 0.003 + 0.003;
  // Initialize the car at progress=0
  const car = new Car(0, speed, road.id, lane);
  lane.cars.push(car);
}

// Spawn cars periodically on each road
setInterval(() => {
  roads.forEach(road => {
    if (Math.random() < 0.8) {
      spawnCar(road);
    }
  });
}, 1500);

// ----- UPDATE -----

function isEWRoad(roadId) {
  return ewLight.origins.includes(roadId);
}

function updateCars() {
  // For each lane, update all cars' positions
  roads.forEach(road => {
    road.lanes.forEach(lane => {
      // Sort cars from front to back
      lane.cars.sort((a, b) => b.progress - a.progress);

      lane.cars.forEach((car, index) => {
        const isApproachingStopLine = (car.progress <= stopLine);

        // Determine if the light is green or red for this road
        let lightIsGreen = true;
        if (isEWRoad(road.id)) {
          lightIsGreen = ewLight.state;
        }

        if (isApproachingStopLine && !lightIsGreen) {
          // Car must stop at the stopLine or behind the next car
          let targetStop = stopLine;
          if (index > 0) {
            const frontCar = lane.cars[index - 1];
            targetStop = Math.min(frontCar.progress - safeGap, stopLine);
          }
          if (car.progress < targetStop) {
            car.progress = Math.min(car.progress + car.speed, targetStop);
          }
        } else {
          // Keep moving forward, maintaining safe gap
          if (index > 0) {
            const frontCar = lane.cars[index - 1];
            if (frontCar.progress - car.progress < safeGap) {
              return; // do nothing if too close
            }
          }
          car.progress += car.speed;
        }
      });

      // Remove cars that have fully crossed the simulation area
      lane.cars = lane.cars.filter(car => car.progress <= 1);
    });
  });
}

// ----- DRAW FUNCTIONS -----

function drawRoads() {
  // For each road, draw a thick gray band with lane dividers
  roads.forEach(road => {
    const centerY = road.start.y;
    const roadHeight = 100; // Bigger roads
    const halfH = roadHeight / 2;

    // Road gradient
    const grad = ctx.createLinearGradient(0, centerY - halfH, 0, centerY + halfH);
    grad.addColorStop(0, '#666');
    grad.addColorStop(1, '#333');

    ctx.fillStyle = grad;
    ctx.fillRect(0, centerY - halfH, canvas.width, roadHeight);

    // Lane dividers
    ctx.save();
    ctx.strokeStyle = '#fff';
    ctx.setLineDash([12, 12]); // Slightly bigger dash
    ctx.lineWidth = 3;        // Thicker lane lines
    for (let i = 1; i < road.laneCount; i++) {
      const laneY = centerY - halfH + (i * (roadHeight / road.laneCount));
      ctx.beginPath();
      ctx.moveTo(0, laneY);
      ctx.lineTo(canvas.width, laneY);
      ctx.stroke();
    }
    ctx.restore();
  });
}

function drawCars() {
  roads.forEach(road => {
    road.lanes.forEach(lane => {
      lane.cars.forEach(car => {
        // Position along the road
        const posX = road.start.x + (road.end.x - road.start.x) * car.progress;
        const posY = road.start.y + (road.end.y - road.start.y) * car.progress;
        // Lane offset
        const offsetX = road.perp.x * lane.offset;
        const offsetY = road.perp.y * lane.offset;

        ctx.save();
        ctx.translate(posX + offsetX, posY + offsetY);
        ctx.rotate(road.angle);

        // Car body
        ctx.fillStyle = car.color;
        ctx.fillRect(-car.length / 2, -car.width / 2, car.length, car.width);

        // Windshield
        ctx.fillStyle = '#ddd';
        ctx.fillRect(
          car.length / 4 - car.length / 2,
          -car.width / 2 + 2,
          car.length / 4,
          car.width - 4
        );

        // Wheels
        ctx.fillStyle = '#000';
        const wheelRadius = 4; // Larger wheels
        // front wheels
        ctx.beginPath();
        ctx.arc(car.length / 4 - car.length / 2, car.width / 2, wheelRadius, 0, 2 * Math.PI);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(car.length / 4 - car.length / 2, -car.width / 2, wheelRadius, 0, 2 * Math.PI);
        ctx.fill();
        // rear wheels
        ctx.beginPath();
        ctx.arc(-car.length / 4, car.width / 2, wheelRadius, 0, 2 * Math.PI);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(-car.length / 4, -car.width / 2, wheelRadius, 0, 2 * Math.PI);
        ctx.fill();

        ctx.restore();
      });
    });
  });
}

/**
 * Draw traffic lights exactly where cars stop (progress = stopLine).
 * We iterate over each Road the light controls, compute the position at stopLine,
 * and draw the red/green circle there.
 */
function drawTrafficLights() {
  roads.forEach(road => {
    // If this road is controlled by the east/west light, place the traffic light at stopLine
    if (ewLight.origins.includes(road.id)) {
      // We'll place the light circle exactly at p = stopLine (0.45).
      const p = stopLine + 0.05;
      const lightX = road.start.x + (road.end.x - road.start.x) * p;
      const lightY = road.start.y + (road.end.y - road.start.y) * p;

      ctx.save();
      ctx.shadowColor = ewLight.state ? 'lime' : 'red';
      ctx.shadowBlur = 15;
      ctx.fillStyle = ewLight.state ? 'lime' : 'red';
      ctx.beginPath();
      ctx.arc(lightX, lightY, 15, 0, 2 * Math.PI); // Larger radius
      ctx.fill();
      ctx.restore();
    }
  });
}

function draw() {
  // Clear then paint a light background
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#f0f0f0';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  drawRoads();
  drawTrafficLights();
  drawCars();
}

// ----- ANIMATION LOOP -----
function animate() {
  updateCars();
  draw();
  requestAnimationFrame(animate);
}

// Start the simulation!
animate();