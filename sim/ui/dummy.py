# ascii_ui.py
import os
import threading
import time

from sim.Sim import Sim
from utils.Junction import Junction
from utils.Lane import Lane
from utils.Road import Road
from utils.TrafficLight import TrafficLight


class AsciiUI:
    def __init__(self, sim: Sim, refresh_rate: float = 1.0):
        """
        :param sim: The simulation object
        :param refresh_rate: How often (in seconds) we refresh the ASCII display
        """
        self.sim = sim
        self.refresh_rate = refresh_rate
        self._stop_ui = threading.Event()

    def start(self):
        """
        Starts a background thread that regularly prints ASCII state
        until stop_ui is set or the simulation stops.
        """
        t = threading.Thread(target=self._run_ui, daemon=True)
        t.start()

    def stop(self):
        self._stop_ui.set()

    def _run_ui(self):
        while not self._stop_ui.is_set():
            self._print_state()
            time.sleep(self.refresh_rate)

    def _print_state(self):
        # Clear the console (works in many terminals; you can remove if undesired)
        os.system('cls' if os.name == 'nt' else 'clear')

        junctions = self.sim.get_junctions()
        for junc in junctions:
            print(f"Junction {junc.get_id()}")

            # Print traffic light states
            for tl in junc.get_traffic_lights():
                light_char = "G" if tl.get_state() else "R"
                print(f"   TrafficLight {tl.get_id()}: {light_char} (origins={tl.get_origins()})")

            # Now print roads & lanes
            for road in junc.get_roads():
                print(f"   Road {road.get_id()}:")
                for lane in road.get_lanes():
                    ascii_lane = self._lane_to_ascii(lane)
                    print(f"      Lane {lane.get_id()}: {ascii_lane}")

        print("\n(Press Ctrl+C to stop)")

    def _lane_to_ascii(self, lane: Lane) -> str:
        """
        Build a string of length ~ lane.LENGTH
        Then mark each car with a character based on car type.
        Because your car distance is from the end, we invert index = (lane.LENGTH - 1) - int(car.dist).
        """
        length = lane.LENGTH
        row = ["-"] * length  # each char is '-'

        for car in lane.get_cars():
            # compute a position in [0, length-1]
            pos = int((lane.LENGTH - 1) - car.get_dist())
            if pos < 0:
                pos = 0
            elif pos >= length:
                pos = length - 1

            # Mark it
            symbol = "C"
            if car.get_car_type().lower().startswith("a"):  # e.g. "AMBULANCE"
                symbol = "A"
            row[pos] = symbol

        return "".join(row)


def main():
    # 1. Create a simple test scenario
    j1 = Junction(id=1)

    # A road with 1 lane
    r1 = Road(id=100)
    lane1 = Lane(
        id=101,
        lane_len=30,
        lane_max_vel=5.0,
        car_creation=0.5  # ~ moderate creation rate
    )
    r1.lanes.append(lane1)

    # Add a traffic light that is green for this lane
    t1 = TrafficLight(id=200, origins=[101], state=True)
    j1.traffic_lights.append(t1)

    j1.roads.append(r1)

    # 2. Create and start the simulation
    sim = Sim([j1], if_ui=True)
    sim.start()

    # 3. Create and start the ASCII UI
    ui = AsciiUI(sim, refresh_rate=0.5)  # refresh twice per second
    ui.start()

    # 4. Let it run until user kills process
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("Stopping UI and simulation...")
        ui.stop()
        sim.stop()


if __name__ == "__main__":
    main()
