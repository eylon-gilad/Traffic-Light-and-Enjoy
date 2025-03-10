import time

from algo.Algorithms.BaseAlgorithm import BaseAlgorithm
from algo.TrafficLightsCombinator import TrafficLightsCombinator

from utils.TrafficLight import TrafficLight
from utils.Junction import Junction
from utils.Road import Road
from utils.RoadEnum import RoadEnum
from utils.Lane import Lane
from utils.Car import Car

from typing import List, Dict
from collections import defaultdict

import numpy as np

class ExpCarsOnTimeController(BaseAlgorithm):

    def __init__(self, junction: Junction):
        super().__init__(junction)
        self.epsilon = 0.01
        self.cars_time_tracker = defaultdict()
        self.combinations = TrafficLightsCombinator(junction).get_combinations()
        for comb in self.combinations:
            self.cars_time_tracker[comb] = defaultdict()

    def start(self):
        while True:
            self.remove_unrelevant_cars()
            self.set_cars_time()
            self.calc_costs()
            print(self.cars_time_tracker)
            if self.costs:
                traffic_lights_max_cost_ids = max(self.costs, key=self.costs.get)
                for traffic_light in self.junction.get_traffic_lights():
                    if traffic_light.get_id() in traffic_lights_max_cost_ids:
                        traffic_light.green()
                    else:
                        traffic_light.red()

    def remove_unrelevant_cars(self):
        to_delete = []
        for traffic_lights_comb in self.cars_time_tracker:
            for car_id in self.cars_time_tracker[traffic_lights_comb]:
                roads = self.junction.get_roads()
                lanes = np.concatenate([road.get_lanes() for road in roads])
                cars = np.concatenate([lane.get_cars() for lane in lanes])
                cars_ids = [car.get_id() for car in cars]
                if car_id not in cars_ids:
                    to_delete.append(car_id)
        for traffic_lights_comb in self.cars_time_tracker:
            for need_to_delete in to_delete:
                if need_to_delete in self.cars_time_tracker[traffic_lights_comb]:
                    del self.cars_time_tracker[traffic_lights_comb][need_to_delete]
        print(to_delete)

    def calc_costs(self):
        self.costs = defaultdict()
        for traffic_lights_comb in self.cars_time_tracker:
            time_sum = 0
            count_cars = 0
            for car_id in self.cars_time_tracker[traffic_lights_comb]:
                time_sum += self.cars_time_tracker[traffic_lights_comb][car_id][0]
                count_cars += 1
            if count_cars != 0:
                self.costs[traffic_lights_comb] = [(count_cars+1)**(time_sum / count_cars)]

    def set_cars_time(self):
        for comb in self.combinations:
            for traffic_light_id in comb:
                origins = self.junction.get_traffic_light_by_id(traffic_light_id).get_origins()
                road_id = origins[0] // 10
                road = self.junction.get_road_by_id(road_id)
                for lane in road.get_lanes_by_ids(origins):
                    for car in lane.cars:
                        if car.get_id() not in self.cars_time_tracker[comb]:
                            self.cars_time_tracker[comb][car.get_id()] = [0, time.time()]  # [delta, start]
                        else:
                            car_started_time = self.cars_time_tracker[comb][car.get_id()][1]
                            self.cars_time_tracker[comb][car.get_id()] = [time.time() - car_started_time, car_started_time]
