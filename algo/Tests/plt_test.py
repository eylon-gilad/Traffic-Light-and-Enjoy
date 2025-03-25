import plotly.express as px
import pandas as pd
from typing import Dict, List

# If you have separate definitions:
# from utils.Junction import Junction
# from utils.Car import Car


class Statistics:
    """
    Collects statistics about cars in the simulation and provides Plotly-based plots.
    """

    def __init__(self):
        # Maps car_id -> time_in_sim so far
        self.car_to_time_in_sim: Dict[int, float] = {}

        # Maps road_id -> list of car counts, one entry per iteration
        self.cars_per_road_history: Dict[int, List[int]] = {}

        # Simple iteration counter (for your reference)
        self.iteration_count = 0

    def plot(self, junction):
        """
        Called to update stats and optionally create plots.
        Typically called once per simulation iteration (or a subset of them).
        """
        self.update_cars_times(junction)
        self.update_cars_roads(junction)

        # Example: only plot every 50th iteration to avoid too many popups
        if self.iteration_count % 50 == 0:
            self.plot_car_time()
            self.plot_cars_in_roads()

        self.iteration_count += 1

    def update_cars_times(self, junction):
        """
        Update how long each car has been in the simulation.
        In this example, we assume 1 iteration = 1 second.
        Adjust 'delta_t' if you use a different time-step.
        """
        delta_t = 1.0

        # Gather all cars in all lanes of all roads for this junction
        all_cars = []
        for road in junction.get_roads():
            for lane in road.get_lanes():
                all_cars.extend(lane.get_cars())

        # Update or initialize times
        for car in all_cars:
            if car.get_id() not in self.car_to_time_in_sim:
                self.car_to_time_in_sim[car.get_id()] = 0.0
            self.car_to_time_in_sim[car.get_id()] += delta_t

        # Optional: remove cars no longer in sim if you only want active cars tracked:
        # current_ids = {car.get_id() for car in all_cars}
        # old_ids = set(self.car_to_time_in_sim.keys()) - current_ids
        # for cid in old_ids:
        #     del self.car_to_time_in_sim[cid]

    def update_cars_roads(self, junction):
        """
        Record how many cars are currently in each road at this iteration.
        """
        for road in junction.get_roads():
            road_id = road.get_id()
            num_cars_in_road = sum(len(lane.get_cars()) for lane in road.get_lanes())

            if road_id not in self.cars_per_road_history:
                self.cars_per_road_history[road_id] = []
            self.cars_per_road_history[road_id].append(num_cars_in_road)

    def plot_car_time(self):
        """
        Creates and shows a Plotly histogram of car times in the sim.
        """
        times = list(self.car_to_time_in_sim.values())
        if not times:
            return  # no data

        df = pd.DataFrame({'time_in_sim': times})
        fig = px.histogram(
            df,
            x='time_in_sim',
            nbins=20,
            title="Distribution of Car Times in Simulation"
        )
        fig.update_layout(
            xaxis_title="Time in Simulation (s)",
            yaxis_title="Number of Cars"
        )
        fig.show()  # or fig.write_html("car_time.html")

    def plot_cars_in_roads(self):
        """
        Creates and shows a Plotly line chart of (iteration vs. #cars) for each road.
        """
        if not self.cars_per_road_history:
            return  # no data

        # Gather data: each row is (iteration, road_id, count)
        rows = []
        for road_id, counts in self.cars_per_road_history.items():
            for i, count in enumerate(counts):
                rows.append((i, road_id, count))

        df = pd.DataFrame(rows, columns=["iteration", "road_id", "car_count"])
        # Convert numeric road_ids to string to label them distinctly
        df["road_id"] = df["road_id"].astype(str)

        fig = px.line(
            df,
            x="iteration",
            y="car_count",
            color="road_id",
            title="Number of Cars in Each Road Over Time"
        )
        fig.update_layout(
            xaxis_title="Iteration",
            yaxis_title="Number of Cars"
        )

        fig.show()  # or fig.write_html("cars_in_roads.html")
