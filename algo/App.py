from flask import Flask, request
from utils.Junction import Junction
from utils.Road import Road
from utils.RoadEnum import RoadEnum
from utils.Lane import Lane
from utils.Car import Car
from utils.TrafficLight import TrafficLight

app = Flask(__name__)

junction = None


@app.route('/junction-info', methods=['Post'])
def post_junction_info():
    global junction

    data = request.get_json()
    junction = data.get('junction')
    roads = (road for road in junction.get('roads'))
    lanes = [lane for road in roads for lane in road]
    cars = [car for road in roads for lane in road for car in lane]
    traffic_lights = [traffic_light for traffic_light in junction.get('traffic_lights')]

    cars = [Car(id=car.get('car_index'), dist=car.get('dist'), velocity=car.get('velocity'), dest=car.get('dest'), car_type=car.get('car_type')) for car in cars]
    lanes = [Lane(id=lane.get('lane_index'), cars=cars) for lane in lanes]
    roads = [Road(id=road.get('road_index'), lanes=lanes, congection_level=road.get('congection_level')) for road in roads]
    traffic_lights = [TrafficLight(id=traffic_light.get('traffic_light_index'), origins=traffic_light.get('input_index'), destinations=traffic_light.get('output_index')) for traffic_light in traffic_lights]
    junction = Junction(traffic_lights=traffic_lights, roads=roads)


@app.route('/traffic-light-state', methods=['Get'])
def get_traffic_light_state():
    global junction
    #algo(junciton)



if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)
