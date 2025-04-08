# 🚦 Traffic Light and Enjoy

**Traffic Light and Enjoy** is a real-time, intelligent traffic simulation framework built with Python. It integrates a Pygame-based simulation engine, a Dash-powered analytics dashboard, and an algorithmic server that supports multiple smart traffic light controllers.

---

## 🔧 Core Features

- **Live Traffic Simulation:** Cars, roads, lanes, and intersections dynamically rendered with collision logic.
- **Smart Controllers:** Multiple traffic light scheduling algorithms, from basic round-robin to fairness-aware adaptive control.
- **Analytics Dashboard:** Real-time insights on car throughput, collisions, speed, and congestion patterns using Plotly Dash.
- **Modular Design:** Easily plug-and-play different traffic control strategies via a unified interface.

---

## 📁 Project Structure

```
Traffic-Light-and-Enjoy/
├── main.py                     # Entry point for the Pygame simulation
├── Sim.py                      # Main simulation loop and traffic logic
├── Client.py                   # Sends traffic data to the dashboard
├── App.py                      # Flask API server for traffic light algorithms
├── AlgoRunner.py               # Executes selected controller logic
├── TrafficLightsCombinator.py  # Valid combinations of traffic lights
├── app.py                      # Dash analytics frontend
├── pages/                      # Dash pages for each visualization
├── algo/Algorithms/            # All traffic control strategies
├── utils/, sim/                # Junction, Road, Car, Light, Lane classes
├── assets/                     # Car images, background, etc.
└── .venv/                      # Local virtual environment
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 🧠 Available Controllers

Each controller inherits from `BaseAlgorithm`. Swap in `AlgoRunner.py`:

```python
# Choose a strategy
self.controller = SmartTrafficController(junction)
```

| Controller                        | Description |
|----------------------------------|-------------|
| `SmartTrafficController`         | Fairness-aware adaptive control with hysteresis. |
| `RoundRobinController`           | Simple, fixed-interval light rotation. |
| `VolumeBasedController`          | Prioritizes busiest roads. |
| `AdaptiveFlowController`         | Smooths wait time updates exponentially. |
| `DynamicWeightedTrafficController` | Adds hysteresis to reduce light flicker. |
| `ExpCarsOnTimeController`        | Experimental: exponential cost for wait time. |
| `wightedAvg`                     | Average wait-based exponential scoring. |

---

## 💡 How to Run

### 1. Start the Algorithm Server

```bash
python App.py
```
Runs on `http://localhost:8080`

### 2. Start the Analytics Dashboard

```bash
python app.py
```
Visit `http://localhost:8050` in your browser

### 3. Start the Simulation

```bash
python main.py
```

> Press `D` for debug overlay. Press `ESC` to quit.

---

## 📊 Dashboard Pages

- **Page 1** – Car lifetime histogram
- **Page 2** – Cars per road over time
- **Page 3** – Lane speed monitoring
- **Page 4** – Collision tracking
- **Page 5** – Correlation heatmap: load vs. velocity

---

## 🙌 Credits

Created by:

- **Eylon Gilad**
- **Stefan Zalman**
- **Eden Gertsman**
- **Elad Sandovski**
- **Ofek Primor**

מכינה אקדמית גאמא מחזור ו

---

