// js/simulation/Spawner.js
import Car from "../entities/Car.js";
import { DESIRED_SPEED } from "../utils/config.js";

/**
 * The Spawner is responsible for adding new cars to the simulation.
 */
export default class Spawner {
  constructor(roads) {
    this.roads = roads;
  }

  spawnCars() {
    this.roads.forEach((road) => {
      if (Math.random() < 0.5) {
        this.spawnCarOnRoad(road);
      }
    });
  }

  spawnCarOnRoad(road) {
    // Choose one of the road’s lanes at random.
    const lane = road.lanes[Math.floor(Math.random() * road.lanes.length)];
    const positionProgress = -1; // Start off–screen.
    const baseSpeed = DESIRED_SPEED;
    const car = new Car(positionProgress, baseSpeed, lane);
    car.desiredSpeed = baseSpeed;
    lane.cars.push(car);
  }
}
