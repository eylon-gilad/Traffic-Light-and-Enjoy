from flask import Flask, request
from utils.Junction import Junction

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
# }
@app.route('/junction-info', methods=['Post'])
def post_junction_info():
    data = request.get_json()


    junc =


@app.route('/traffic-light-state', methods=['Get'])
def get_traffic_light_state():
    pass


if __name__ == '__main__':
    app.run(debug=True)
