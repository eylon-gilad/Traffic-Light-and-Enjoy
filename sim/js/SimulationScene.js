// js/SimulationScene.js
import SimulationManager from "./simulation/simulationManager.js";
import Renderer from "./render/Renderer.js";
import Spawner from "./simulation/Spawner.js";
import { createRoads } from "./entities/createRoads.js";

export default class SimulationScene extends Phaser.Scene {
  constructor() {
    super({ key: "SimulationScene" });
  }

  preload() {
    // Load assets (for example, a car sprite and several variations)
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
    // Enlarge the road width.
    this.roadWidth = 180;
    this.centerX = this.canvasWidth / 2;
    this.centerY = this.canvasHeight / 2;

    // Create the four roads.
    this.roads = createRoads(this.centerX, this.centerY, this.canvasWidth, this.canvasHeight, this.roadWidth);

    // Setup simple traffic lights.
    // For NS roads, nsTrafficLight is defined; for EW roads, ewTrafficLight is defined.
    this.roads.forEach((road) => {
      if (road.id === "north" || road.id === "south") {
        road.nsTrafficLight = {
          state: true,
          isGreen() { return this.state; },
          toggle() { this.state = !this.state; }
        };
      } else {
        road.ewTrafficLight = {
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

    // Define the traffic–light cycle function using an arrow function to bind 'this'
    this.scheduleTrafficLightsCycle = () => {
      // At t = 0s: NS green, EW red.
      this.roads.forEach((road) => {
        if (road.id === "north" || road.id === "south") {
          if (road.nsTrafficLight) road.nsTrafficLight.state = true;
        } else {
          if (road.ewTrafficLight) road.ewTrafficLight.state = false;
        }
      });

      // At t = 3s: both red.
      this.time.delayedCall(3000, () => {
        this.roads.forEach((road) => {
          if (road.nsTrafficLight) road.nsTrafficLight.state = false;
          if (road.ewTrafficLight) road.ewTrafficLight.state = false;
        });
      }, [], this);

      // At t = 4s: NS red, EW green.
      this.time.delayedCall(4000, () => {
        this.roads.forEach((road) => {
          if (road.id === "north" || road.id === "south") {
            if (road.nsTrafficLight) road.nsTrafficLight.state = false;
          } else {
            if (road.ewTrafficLight) road.ewTrafficLight.state = true;
          }
        });
      }, [], this);

      // At t = 7s: both red.
      this.time.delayedCall(7000, () => {
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
      delay: 8000,
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
