// js/SimulationScene.js
import SimulationManager from "./simulation/simulationManager.js";
import Renderer from "./render/Renderer.js";
import Spawner from "./simulation/Spawner.js";
import { createRoads } from "./entities/createRoads.js";

// Global counter for traffic lights.
let nextTrafficLightId = 1;

export default class SimulationScene extends Phaser.Scene {
  constructor() {
    super({ key: "SimulationScene" });
  }

  preload() {
    // Load assets for cars.
    this.load.image("carSprite", "assets/red-car.png");
    this.load.image("carSprite1", "assets/car1.png");
    this.load.image("carSprite2", "assets/car2.png");
    this.load.image("carSprite3", "assets/car3.png");
    this.load.image("carSprite4", "assets/car4.png");
    this.load.image("carSprite5", "assets/car5.png");
    this.load.image("carSprite6", "assets/car6.png");
    this.load.image("carSprite7", "assets/car7.png");
  }

  create() {
    this.graphics = this.add.graphics();
    this.canvasWidth = this.sys.game.config.width;
    this.canvasHeight = this.sys.game.config.height;
    this.roadWidth = 180;
    this.centerX = this.canvasWidth / 2;
    this.centerY = this.canvasHeight / 2;

    // Create roads (notice we no longer pass an id; the Road constructor will generate its own).
    this.roads = createRoads(this.centerX, this.centerY, this.canvasWidth, this.canvasHeight, this.roadWidth);

    // NEW: assign right turn destinations.
    this.assignRightTurnDestinations(this.roads);


    // Setup traffic lights.
    // For each road, if it is a "north" or "south" road, create a NS traffic light;
    // otherwise create an EW traffic light.
    // Here we assign each traffic light an ID like "TLE-TL1", "TLE-TL2", etc.
    this.roads.forEach((road) => {
      if (road.id.includes("R1") || road.id.includes("R2")) {
        // For demonstration, assume these are NS roads.
        road.nsTrafficLight = {
          id: `TLE-TL${nextTrafficLightId++}`,
          state: true,
          isGreen() { return this.state; },
          toggle() { this.state = !this.state; }
        };
      } else {
        // Otherwise, EW roads.
        road.ewTrafficLight = {
          id: `TLE-TL${nextTrafficLightId++}`,
          state: false,
          isGreen() { return this.state; },
          toggle() { this.state = !this.state; }
        };
      }
    });

    // Create simulation, renderer, and spawner managers.
    this.simulationManager = new SimulationManager(this.roads);
    this.rendererManager = new Renderer(this, this.roads);
    this.spawner = new Spawner(this.roads);

    // Periodically spawn cars.
    this.time.addEvent({
      delay: 500,
      callback: () => this.spawner.spawnCars(),
      loop: true,
    });

    // Define a traffic light cycle (details omitted for brevity).
    this.scheduleTrafficLightsCycle = () => {
      // For each road, set the traffic light state (this example simply toggles states).

      // At t = 0s: NS green, EW red.
      this.roads.forEach((road) => {
        if (road.nsTrafficLight) road.nsTrafficLight.state = true;
        if (road.ewTrafficLight) road.ewTrafficLight.state = false;
      });

      // At t = 3s: both red.
      this.time.delayedCall(4000, () => {
        this.roads.forEach((road) => {
          if (road.nsTrafficLight) road.nsTrafficLight.state = false;
          if (road.ewTrafficLight) road.ewTrafficLight.state = false;
        });
      }, [], this);

      // At t = 4s: NS red, EW green.
      this.time.delayedCall(5000, () => {
        this.roads.forEach((road) => {
          if (road.nsTrafficLight) road.nsTrafficLight.state = false;
          if (road.ewTrafficLight) road.ewTrafficLight.state = true;
        });
      }, [], this);

      // At t = 7s: both red.
      this.time.delayedCall(9000, () => {
        this.roads.forEach((road) => {
          if (road.nsTrafficLight) road.nsTrafficLight.state = false;
          if (road.ewTrafficLight) road.ewTrafficLight.state = false;
        });
      }, [], this);
    };

    // Run the cycle immediately.
    this.scheduleTrafficLightsCycle();

    // Then schedule it to repeat every 8 seconds.
    this.time.addEvent({
      delay: 10000,
      callback: this.scheduleTrafficLightsCycle,
      callbackScope: this,
      loop: true
    });

    // Setup control panel buttons (pause and reset).
    this.simulationPaused = false;
    this.setupControls();

    // Resume audio on first user interaction.
    this.input.once("pointerdown", () => {
      if (this.sound && this.sound.context && this.sound.context.state !== "running") {
        this.sound.context.resume();
      }
    });
  }

  // In your SimulationScene.js, after creating roads...
  assignRightTurnDestinations(roads) {
    // Assumed mapping:
    // - Road 1 ("TLE-R1", northbound) → right turn into rightmost lane of Road 4 ("TLE-R4", eastbound)
    // - Road 2 ("TLE-R2", southbound) → right turn into rightmost lane of Road 3 ("TLE-R3", westbound)
    // - Road 3 ("TLE-R3", eastbound)  → right turn into rightmost lane of Road 1 ("TLE-R1", southbound)
    // - Road 4 ("TLE-R4", westbound)  → right turn into rightmost lane of Road 2 ("TLE-R2", northbound)
    
    // For convenience, build a lookup by road id.
    const roadLookup = {};
    roads.forEach(road => roadLookup[road.id] = road);

    roads.forEach(road => {
      // Get the rightmost lane (the lane with highest index).
      const rightLane = road.lanes[road.lanes.length - 1];
      // Determine the destination road based on this road's id.
      let destRoad = null;
      if (road.id === "TLE-R1") {
        destRoad = roadLookup["TLE-R4"];
      } else if (road.id === "TLE-R2") {
        destRoad = roadLookup["TLE-R3"];
      } else if (road.id === "TLE-R3") {
        destRoad = roadLookup["TLE-R1"];
      } else if (road.id === "TLE-R4") {
        destRoad = roadLookup["TLE-R2"];
      }
      // If a destination road is found, assign its rightmost lane as the destination.
      if (destRoad) {
        rightLane.destinationLanes = [destRoad.lanes[destRoad.lanes.length - 1]];
      }
      // (For non–rightmost lanes, destinationLanes remains as [this].)
    });
  }

  setupControls() {
    const toggleBtn = document.getElementById("toggleBtn");
    toggleBtn.addEventListener("click", () => {
      this.simulationPaused = !this.simulationPaused;
    });
    const resetBtn = document.getElementById("resetBtn");
    resetBtn.addEventListener("click", () => {
      this.roads.forEach((road) => {
        road.lanes.forEach((lane) => {
          lane.cars = [];
          // Optionally, reset lane.nextCarId if you want to restart numbering.
          lane.nextCarId = 1;
        });
      });
    });
  }

  update(time, delta) {
    if (!this.simulationPaused) {
      this.simulationManager.update(delta);
    }
    this.rendererManager.render();
  }
}
