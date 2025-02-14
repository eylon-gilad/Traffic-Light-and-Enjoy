// js/utils/config.js
// All units for dynamic calculations are in pixels and seconds.
// (Road lengths are in pixels; car speeds are stored in “normalized” units,
// so that speed × roadLength gives pixels per second.)

export const SAFE_DISTANCE_PIXELS = 100;        // minimum bumper-to-bumper gap (in pixels)
export const TIME_HEADWAY = 1.5;                  // desired time gap (seconds)
export const MAX_ACCELERATION = 300;              // maximum acceleration (pixels per second²)
export const COMFORTABLE_DECELERATION = 400;      // comfortable deceleration (pixels per second²)
export const DESIRED_SPEED = 0.5;                 // normalized desired speed (multiplied by roadLength gives pixels/sec)
export const IDM_DELTA = 4;                       // acceleration exponent (IDM parameter)
export const ANTICIPATION_FACTOR = 0.5;           // How much the gap beyond the immediate car influences braking.
export const NOISE_AMPLITUDE = 0.05;              // Amplitude of random fluctuations (fraction of a_max)
