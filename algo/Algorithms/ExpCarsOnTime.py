import time

from BaseAlgorithm import BaseAlgorithm
from algo.TrafficLightsCombinator import TrafficLightsCombinator

from utils.TrafficLight import TrafficLight
from utils.Junction import Junction
from utils.Road import Road
from utils.RoadEnum import RoadEnum
from utils.Lane import Lane
from utils.Car import Car

from typing import List, Dict
from collections import defaultdict


class ExpCarsOnTimeController(BaseAlgorithm):

    def __init__(self, junction: Junction):
        super().__init__(junction)
        self.cars_time_tracker = defaultdict()
        self.combinations = TrafficLightsCombinator.combination
        for comb in self.combinations:
            self.cars_time_tracker[comb] = defaultdict()

    def start(self):
        while True:
            self.set_cars_time()
            self.calc_costs()
            traffic_lights_max_cost_ids = max(self.costs, key=self.costs.get)
            for traffic_light in self.junction.get_traffic_lights():
                if traffic_light.get_id() in traffic_lights_max_cost_ids:
                    traffic_light.green()
                else:
                    traffic_light.red()

    def calc_costs(self):
        self.costs = defaultdict()
        for traffic_lights_comb in self.cars_time_tracker:
            time_sum = 0
            count_cars = 0
            for car_time in traffic_lights_comb:
                time_sum += self.cars_time_tracker[traffic_lights_comb][car_time][0]
                count_cars += 1
            self.costs[traffic_lights_comb] = [count_cars**(time_sum / count_cars)]


    def set_cars_time(self):
        for comb in self.combinations:
            for traffic_light_id in comb:
                for origins in self.junction.get_traffic_light_by_id(traffic_light_id):
                    road_id = origins[0] // 10
                    road = self.junction.get_road_by_id(road_id)
                    for lane in road.get_lanes_by_ids(origins):
                        for car in lane.cars:
                            if car.get_id() not in self.cars_time_tracker[comb]:
                                self.cars_time_tracker[comb][car.get_id()] = [0, time.time()]  # [delta, start]
                            else:
                                car_started_time = self.cars_time_tracker[comb][car.get_id()][1]
                                self.cars_time_tracker[comb][car.get_id()] = [time.time() - car_started_time, car_started_time]

