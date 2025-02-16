// js/simulation/SimulationManager.js
import { roadLength, distanceToStopLine } from "../utils/utils.js";
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
 */
export default class SimulationManager {
  constructor(roads) {
    this.roads = roads;
  }

  update(delta) {
    // Convert delta from ms to seconds.
    const dt = delta / 1000;
    this.roads.forEach(road => {
      const roadLen = roadLength(road);
      road.lanes.forEach(lane => {
        // Sort cars with the front-most first.
        lane.cars.sort((a, b) => b.positionProgress - a.positionProgress);
        lane.cars.forEach((car, index) => {
          // Compute the current position (in pixels).
          const pos_px = car.positionProgress * roadLen;

          // === Compute Gap to Immediate Front Car ===
          let gap1 = Infinity;
          let v1 = 0; // speed of immediate front car (pixels/sec)
          if (index > 0) {
            const frontCar = lane.cars[index - 1];
            const frontPos_px = frontCar.positionProgress * roadLen;
            gap1 = frontPos_px - pos_px;
            v1 = frontCar.speed * roadLen;
          }

          // === Incorporate Anticipation: Look Ahead to the Second Car ===
          let gap2 = 0; // gap from first to second car
          let v2 = 0;   // speed of the second car (pixels/sec)
          if (index > 1) {
            const secondCar = lane.cars[index - 2];
            const frontCar = lane.cars[index - 1];
            gap2 = (secondCar.positionProgress * roadLen) - (frontCar.positionProgress * roadLen);
            v2 = secondCar.speed * roadLen;
          }

          // Compute an effective gap.
          let effectiveGap = gap1;
          if (gap2 > 0 && gap1 < 200) { // 200 pixels threshold
            effectiveGap += ANTICIPATION_FACTOR * gap2;
          }

          // === Check for a Red Traffic Light Obstacle ===
          let gapLight = Infinity;
          let lightActive = false;
          if (road.nsTrafficLight || road.ewTrafficLight) {
            const light = (road.id === "north" || road.id === "south")
              ? road.nsTrafficLight
              : road.ewTrafficLight;
            if (!light.isGreen() && car.positionProgress < road.stopProgress) {
              gapLight = distanceToStopLine(car, road);
              lightActive = true;
            }
          }

          // Use the smaller of the effective gap and the gap to the stop line.
          const s = Math.min(effectiveGap, gapLight);

          // === Speeds and Desired Speed ===
          const v = car.speed * roadLen;       // current speed in pixels/sec
          const v0 = car.desiredSpeed * roadLen; // desired speed in pixels/sec

          // === IDM Parameters ===
          const s0 = SAFE_DISTANCE_PIXELS; // minimum gap (pixels)
          const T = TIME_HEADWAY;          // desired time gap (seconds)
          const a_max = MAX_ACCELERATION;  // maximum acceleration (pixels/sec²)
          const b = COMFORTABLE_DECELERATION; // comfortable deceleration (pixels/sec²)

          // === Compute Relative Speed (delta_v) ===
          let delta_v = 0;
          if (gap1 < Infinity) {
            delta_v = v - v1;
          }
          if (index > 1) {
            const delta_v2 = v1 - v2;
            delta_v = (delta_v + delta_v2) / 2;
          }

          // === Compute the Desired Dynamic Gap ===
          const s_star = s0 + v * T + (v * Math.max(0, delta_v)) / (2 * Math.sqrt(a_max * b));

          // === IDM Acceleration with Anticipation ===
          let acceleration = a_max * (1 - Math.pow(v / v0, IDM_DELTA) - Math.pow(s_star / s, 2));
          if (s < s0) {
            acceleration = -b;
          }
          // Add a small stochastic fluctuation.
          acceleration += (Math.random() * 2 - 1) * NOISE_AMPLITUDE * a_max;

          // === Kinematic Updates (True Physics) ===
          const new_v = Math.max(v + acceleration * dt, 0); // update speed (pixels/sec)
          const newPos_px = pos_px + v * dt + 0.5 * acceleration * dt * dt; // update position (pixels)

          // Convert back to normalized units.
          car.speed = new_v / roadLen;
          car.positionProgress = newPos_px / roadLen;

          // --- Final Clamp: Enforce Safe Gap at Red Light and Prevent Overshoot ---
          this.finalClamp(car, index, lane, road);
        });
        // Remove cars only if they have gone well off–screen (buffer zone).
        lane.cars = lane.cars.filter(car => car.positionProgress <= 1.1);
      });
    });
  }

  /**
   * Clamp the car’s progress to enforce safe stopping at a red light and to maintain a safe gap.
   * This function is called at the end of each car’s update.
   */
  finalClamp(car, index, lane, road) {
    const roadLen = roadLength(road);
    const s0 = SAFE_DISTANCE_PIXELS;
    // Enforce safe gap to the immediate leader.
    if (index > 0) {
      const leader = lane.cars[index - 1];
      const leaderPos_px = leader.positionProgress * roadLen;
      const carPos_px = car.positionProgress * roadLen;
      if (leaderPos_px - carPos_px < s0) {
        // Adjust position to maintain the safe gap.
        car.positionProgress = (leaderPos_px - s0) / roadLen;
        car.speed = 0;
      }
    }
    // Prevent negative progress.
    if (car.positionProgress < 0) {
      car.positionProgress = 0;
      car.speed = 0;
    }
  }
}
