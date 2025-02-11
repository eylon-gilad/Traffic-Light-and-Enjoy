/**************************************
 *  simulation.js
 **************************************/

// 2. Setup the canvas
const canvas = document.getElementById('simulation');
const ctx = canvas.getContext('2d');
canvas.width = 1600;
canvas.height = 1000;

// 3. Simulation parameters
const stopLine = 0.45; 
const safeGap  = 0.05; 

// 4. Make the traffic lights toggle with opposite states
//    e.g. if lightA becomes !lightA.state, then lightB should be the opposite
setInterval(() => {
  lightA.state = !lightA.state;
  // exactly opposite for lightB
  lightB.state = !lightA.state;
}, 2500);

// 5. Load initial cars onto roads
function loadInitialCars(carList) {
  carList.forEach(cfg => {
    const road = roads.find(r => r.id === cfg.roadId);
    if (!road) {
      console.error(`No road found with ID "${cfg.roadId}"`);
      return;
    }
    if (cfg.laneIndex < 0 || cfg.laneIndex >= road.lanes.length) {
      console.error(`Invalid laneIndex ${cfg.laneIndex} for road "${cfg.roadId}"`);
      return;
    }
    const lane = road.lanes[cfg.laneIndex];
    const car  = new Car(cfg.progress, cfg.speed, cfg.roadId, lane);
    lane.cars.push(car);
  });
}
loadInitialCars(initialCars);

// 6. Helper to see which light controls a given roadId
//    e.g. if roadId is in lightA.origins => it’s controlled by lightA, else by lightB
function getTrafficLightForRoad(roadId) {
  if (lightA.origins.includes(roadId)) return lightA;
  if (lightB.origins.includes(roadId)) return lightB;
  return null; // if no light controls it
}

// 7. Update logic
function updateCars() {
  roads.forEach(road => {
    road.lanes.forEach(lane => {
      // Sort from front to back
      lane.cars.sort((a,b) => b.progress - a.progress);

      lane.cars.forEach((car, index) => {
        const approachingStop = (car.progress <= stopLine);

        // Find which traffic light (if any) controls this road
        let theLight = getTrafficLightForRoad(road.id);
        // Default to green if no light found
        let lightIsGreen = theLight ? theLight.state : true;

        if (approachingStop && !lightIsGreen) {
          // Must stop behind stopLine or behind front car
          let targetStop = stopLine;
          if (index > 0) {
            const frontCar = lane.cars[index - 1];
            targetStop = Math.min(frontCar.progress - safeGap, stopLine);
          }
          if (car.progress < targetStop) {
            car.progress = Math.min(car.progress + car.speed, targetStop);
          }
        } else {
          // Move forward, ensuring safe gap
          if (index > 0) {
            const frontCar = lane.cars[index - 1];
            if (frontCar.progress - car.progress < safeGap) {
              return;
            }
          }
          car.progress += car.speed;
        }
      });

      // Remove cars that have finished
      lane.cars = lane.cars.filter(c => c.progress <= 1);
    });
  });
}

// 8. Check if all cars are done
function allCarsDone() {
  return roads.every(r => 
    r.lanes.every(l => l.cars.length === 0)
  );
}

// 9. Drawing
function drawBackground() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#f0f0f0';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function drawRoads() {
  roads.forEach(road => {
    // We'll assume these roads are horizontal
    const centerY = road.start.y;
    const roadHeight = 100;
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
    ctx.setLineDash([12,12]);
    ctx.lineWidth = 3;
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

function drawTrafficLights() {
  roads.forEach(road => {
    // We'll place the light near p=stopLine if that road is controlled by a light
    const theLight = getTrafficLightForRoad(road.id);
    if (!theLight) return;

    const p = stopLine + 0.05;
    const x = road.start.x + (road.end.x - road.start.x) * p;
    const y = road.start.y + (road.end.y - road.start.y) * p;

    ctx.save();
    ctx.shadowColor = theLight.state ? 'lime' : 'red';
    ctx.shadowBlur = 15;
    ctx.fillStyle = theLight.state ? 'lime' : 'red';
    ctx.beginPath();
    ctx.arc(x, y, 15, 0, 2*Math.PI);
    ctx.fill();
    ctx.restore();
  });
}

function drawCars() {
  roads.forEach(road => {
    road.lanes.forEach(lane => {
      lane.cars.forEach(car => {
        const posX = road.start.x + (road.end.x - road.start.x) * car.progress;
        const posY = road.start.y + (road.end.y - road.start.y) * car.progress;
        const offX = road.perp.x * lane.offset;
        const offY = road.perp.y * lane.offset;

        ctx.save();
        ctx.translate(posX + offX, posY + offY);
        ctx.rotate(road.angle);

        // Car body
        ctx.fillStyle = car.color;
        ctx.fillRect(-car.length/2, -car.width/2, car.length, car.width);

        // Windshield
        ctx.fillStyle = '#ddd';
        ctx.fillRect(
          car.length/4 - car.length/2,
          -car.width/2 + 2,
          car.length/4,
          car.width - 4
        );

        // Wheels
        ctx.fillStyle = '#000';
        const wr = 4; 
        // front wheels
        ctx.beginPath();
        ctx.arc(car.length/4 - car.length/2,  car.width/2, wr, 0, 2*Math.PI);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(car.length/4 - car.length/2, -car.width/2, wr, 0, 2*Math.PI);
        ctx.fill();
        // rear wheels
        ctx.beginPath();
        ctx.arc(-car.length/4,  car.width/2, wr, 0, 2*Math.PI);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(-car.length/4, -car.width/2, wr, 0, 2*Math.PI);
        ctx.fill();

        ctx.restore();
      });
    });
  });
}

function draw() {
  drawBackground();
  drawRoads();
  drawTrafficLights();
  drawCars();
}

// 10. Animation loop
function animate() {
  updateCars();
  draw();

  if (allCarsDone()) {
    console.log("All cars have finished! Simulation done.");
    return;
  }
  requestAnimationFrame(animate);
}

// Start it off!
animate();
