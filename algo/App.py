from flask import Flask, request
from utils.Junction import Junction
from utils.Road import Road
# from utils.RoadEnum import RoadEnum
from utils.Lane import Lane
from utils.Car import Car
from utils.TrafficLight import TrafficLight

app = Flask(__name__)

junction = None


@app.route('/junction-info', methods=['Post'])
def post_junction_info():
    global junction

    data = request.get_json()
    junction = data.get('junction')  # Extracting the junction json from the data.
    traffic_lights = [traffic_light for traffic_light in junction.get('traffic_lights')]  # Extracting the traffic light json from the junction one.
    roads = (road for road in junction.get('roads'))  # Extracting the roads json from the junction one.
    lanes = [lane for road in roads for lane in road]  # Extracting the lanes json from the roads json.
    cars = [car for road in roads for lane in road for car in lane]  # Extracting the cars json from the lanes json.

    cars = [Car(id=car.get('car_index'),
                dist=car.get('dist'),
                velocity=car.get('velocity'),
                dest=car.get('dest'),
                car_type=car.get('car_type'))
            for car in cars]  # Creating a list of car object.

    lanes = [Lane(id=lane.get('lane_index'),
                  cars=cars)
             for lane in lanes]  # Creating a list of lane object.

    roads = [Road(id=road.get('road_index'),
                  lanes=lanes,
                  congection_level=road.get('congection_level'))
             for road in roads]  # Creating a list of road object.

    traffic_lights = [TrafficLight(id=traffic_light.get('traffic_light_index'),
                                   origins=traffic_light.get('input_index'),
                                   destinations=traffic_light.get('output_index'))
                      for traffic_light in traffic_lights]  # Creating a list of traffic light object.

    junction = Junction(traffic_lights=traffic_lights, roads=roads)  # Creating a junction object.


@app.route('/traffic-light-state', methods=['Get'])
def get_traffic_light_state():
    global junction
    # algo(junction)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)
