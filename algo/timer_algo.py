from utils.TrafficLight import TrafficLight
import time
class timer_algo():
    
    def __init__(self):
        self.times=[]
    
    def render_res(self):
        #creating the trafic lights
        pass

    def send_data(self):
        pass



    def change_pos(traffic_lights):
        for traffic_light in traffic_lights:
            traffic_light.toggle()
    
    def algo(self):
        while True:
            self.render_res()
            self.change_pos()
            self.send_data()
            time.sleep(5)

{
 road.timeWait=123   
}