// js/simulation/SimulationManager.js
import { roadLength, distanceToStopLine, pixelsToProgress } from "../utils/utils.js";
import { 
  SAFE_DISTANCE_PIXELS, 
  TIME_HEADWAY, 
  MAX_ACCELERATION, 
  COMFORTABLE_DECELERATION, 
  IDM_DELTA,
  ANTICIPATION_FACTOR,
  NOISE_AMPLITUDE
} from "../utils/config.js";

/**
 * The SimulationManager updates each car’s movement.
 * This advanced model combines an IDM–like formulation with anticipation (looking
 * beyond the immediately leading car) and small stochastic fluctuations.
 * It also includes final clamping routines to prevent overshooting the safe stop line.
 * 
 * In this first step of turning behavior, when a car reaches the junction (i.e. its
 * progress exceeds road.stopProgress) and its lane’s destination (destinationLanes[0])
 * is different from its current lane—and if it has not yet turned—the car is removed 
 * from its current lane and added to the destination lane with a new progress.
 */
export default class SimulationManager {
  constructor(roads) {
    this.roads = roads;
  }

  update(delta) {
    const dt = delta / 1000; // convert ms to seconds

    // Process each road.
    this.roads.forEach(road => {
      const roadLen = roadLength(road);
      road.lanes.forEach(lane => {
        // Use a backward loop so that we can safely remove cars.
        for (let i = lane.cars.length - 1; i >= 0; i--) {
          const car = lane.cars[i];
          // --- Car Update Start ---
          const pos_px = car.positionProgress * roadLen;

          // Compute gap to immediate front car.
          let gap1 = Infinity;
          let v1 = 0; // speed of immediate front car (pixels/sec)
          if (i > 0) {
            const frontCar = lane.cars[i - 1];
            const frontPos_px = frontCar.positionProgress * roadLen;
            gap1 = frontPos_px - pos_px;
            v1 = frontCar.speed * roadLen;
          }

          // Look ahead to the second car.
          let gap2 = 0;
          let v2 = 0;
          if (i > 1) {
            const secondCar = lane.cars[i - 2];
            const frontCar = lane.cars[i - 1];
            gap2 = (secondCar.positionProgress * roadLen) - (frontCar.positionProgress * roadLen);
            v2 = secondCar.speed * roadLen;
          }
          let effectiveGap = gap1;
          if (gap2 > 0 && gap1 < 200) {
            effectiveGap += ANTICIPATION_FACTOR * gap2;
          }

          // Check for a red light obstacle.
          let gapLight = Infinity;
          let lightActive = false;
          if (road.nsTrafficLight || road.ewTrafficLight) {
            const light = (road.id === "TLE-R1" || road.id === "TLE-R2")
              ? road.nsTrafficLight
              : road.ewTrafficLight;
            if (!light.isGreen() && car.positionProgress < road.stopProgress) {
              gapLight = distanceToStopLine(car, road);
              lightActive = true;
            }
          }
          const s = Math.min(effectiveGap, gapLight);

          const v = car.speed * roadLen;
          const v0 = car.desiredSpeed * roadLen;

          // IDM parameters.
          const s0 = SAFE_DISTANCE_PIXELS;
          const T = TIME_HEADWAY;
          const a_max = MAX_ACCELERATION;
          const b = COMFORTABLE_DECELERATION;

          let delta_v = 0;
          if (gap1 < Infinity) {
            delta_v = v - v1;
          }
          if (i > 1) {
            const delta_v2 = v1 - v2;
            delta_v = (delta_v + delta_v2) / 2;
          }
          const s_star = s0 + v * T + (v * Math.max(0, delta_v)) / (2 * Math.sqrt(a_max * b));

          let acceleration = a_max * (1 - Math.pow(v / v0, IDM_DELTA) - Math.pow(s_star / s, 2));
          if (s < s0) {
            acceleration = -b;
          }
          acceleration += (Math.random() * 2 - 1) * NOISE_AMPLITUDE * a_max;

          const new_v = Math.max(v + acceleration * dt, 0);
          const newPos_px = pos_px + v * dt + 0.5 * acceleration * dt * dt;

          car.speed = new_v / roadLen;
          car.positionProgress = newPos_px / roadLen;
          // --- Car Update End ---

          // Turning behavior:
          // Only attempt turning if the car has not yet turned (flag not set)
          // and the car has reached or passed the junction (progress >= stopProgress).
          if (!car.hasTurned && car.positionProgress >= road.stopProgress) {
            const destLane = car.lane.destinationLanes[0];
            if (destLane !== car.lane) {
              // Remove car from current lane.
              lane.cars.splice(i, 1);
              // Set a flag so it won't attempt turning again.
              car.hasTurned = true;
              // Set the car's lane to the destination lane.
              car.lane = destLane;
              // Set car progress to destination road stop progress + offset.
              let newProgress = destLane.road.stopProgress + pixelsToProgress(destLane.road, destLane.road.roadWidth * 2);
              // Clamp newProgress if greater than 0.99.
              if (newProgress > 0.99) newProgress = 0.99;
              car.positionProgress = newProgress;
              // Add the car to the destination lane.
              destLane.cars.push(car);
              console.log(`car ${car.id} turned from ${lane.id} to ${destLane.id} with progress ${car.positionProgress}`);
              continue; // Skip further processing for this car.
            }
          }

          // Finally, apply final clamping.
          this.finalClamp(car, i, lane, road);
        }
        // Remove cars that have gone far off–screen.
        lane.cars = lane.cars.filter(car => car.positionProgress <= 1.1);
      });
    });
  }

  /**
   * Clamp the car’s progress to enforce safe stopping at a red light and to maintain a safe gap.
   * If a car has passed the stop line, no red–light clamping is applied.
   */
  finalClamp(car, index, lane, road) {
    const roadLen = roadLength(road);
    const s0 = SAFE_DISTANCE_PIXELS;
  
    if (index > 0) {
      const leader = lane.cars[index - 1];
      const leaderPos_px = leader.positionProgress * roadLen;
      const carPos_px = car.positionProgress * roadLen;
      if (leaderPos_px - carPos_px < s0) {
        car.positionProgress = (leaderPos_px - s0) / roadLen;
        car.speed = 0;
      }
    }
    if (car.positionProgress < 0) {
      car.positionProgress = 0;
      car.speed = 0;
    }
  }
}
