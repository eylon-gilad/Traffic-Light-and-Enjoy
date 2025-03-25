import random
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
from typing import Dict, List
from utils.Junction import Junction


def main():
    pass


if __name__ == "__main__":
    main()


class Statistics:

    def __init__(self):
        self.car_to_times: Dict[int, List[int]] = {}
        self.num_cars_in_road_history: List[Dict[int, int]] = []
        self.interation = 0

    def plot(self, junction: Junction):
        self.update_cars_times(junction)
        self.update_cars_roads(junction)

        self.plot_car_time()
        self.plot_cars_in_roads()

        self.interation += 1

    def plot_car_time(self):
        pass

    def plot_cars_in_roads(self):
        colors = []
        for num_cars_in_road in self.num_cars_in_road_history:
            for road in num_cars_in_road:
                plt.scatter(self.interation, num_cars_in_road[road])

    def update_cars_times(self, junction: Junction):
        pass

    def update_cars_roads(self, junction: Junction):
        num_cars_in_road: Dict[int, int] = {}
        for road in junction.get_roads():
            for lane in road.get_lanes():
                for car in lane.get_cars():
                    if road.get_id() in num_cars_in_road:
                        num_cars_in_road[road.get_id()] += 1
                    else:
                        num_cars_in_road[road.get_id()] = 1
        self.num_cars_in_road_history.append(num_cars_in_road)





