from flask import Flask, request
from utils.Junction import Junction
from utils.Road import Road
from utils.RoadEnum import RoadEnum
from utils.Lane import Lane
from utils.Car import Car
from utils.TrafficLight import TrafficLight

app = Flask(__name__)

# {
#     "traffic_light": "",  // "Green" or "Red"
#     "junction": {
#         "total_roads": 0,
#         "roads": [
#             {
#                 "road_index": 0,
#                 "num_lanes": 0,
#                 "congestion_level": "",  // "Low", "Moderate", or "High"
#                 "lanes": [
#                     {
#                         "lane_index": 0,
#                         "total_cars": 0,
#                         "cars": [
#                             {
#                                 "dist": [],  // List of float values
#                                 "velocity": 0.0,
#                                 "dest": "",
#                                 "car_type": ""  // "CAR", "AMBULANCE", "PEDESTRIAN"
#                             }
#                         ]
#                     }
#                 ]
#             }
#         ]
#     }
# }\


@app.route('/junction-info', methods=['Post'])
def post_junction_info():
    data = request.get_json()
    traffic_lights = data.get('traffic_lights')
    junction = data.get('junction')
    roads = (road for road in junction.get('roads'))
    lanes = [lane for road in roads for lane in road]
    cars = [car for road in roads for lane in road for car in lane]

    cars = [Car(car.get('car_index'), car.get('dist'), car.get('velocity'), car.get('dest'), car.get('car_type')) for car in cars]
    lanes = [Lane(lane.get('lane_index'), cars[id]) for id, lane in enumerate(lanes)]
    roads = [Road(road.get('road_index'), lanes[id]) for id, road in enumerate(roads)]

    junc = None


@app.route('/traffic-light-state', methods=['Get'])
def get_traffic_light_state():
    pass


if __name__ == '__main__':
    app.run(debug=True)
