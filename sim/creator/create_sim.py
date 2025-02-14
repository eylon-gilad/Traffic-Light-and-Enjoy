import json
import random

def create_light(traffic_light_index:int,input_index:list[int],output_index:list[int],state:bool |None=0):
    """
    create the traffic light object
    input: 
    traffic_light_index,
    inputs_index(the roads the cars are in),
    output_index(roads the car will drive to),
    state(red-0 or green-1)

    output: trafic light object
    """
    traffic_light={}
    traffic_light["traffic_light_index"]=traffic_light_index
    traffic_light["input_index"]=input_index
    traffic_light["output_index"]=output_index
    traffic_light["state"]=state
    return traffic_light


def create_all_lights(amount_road:int |None=4,black_list: list[tuple[int]]| None = [],merged_lights: list[tuple[list,list]]| None = [([],[])] ):
    """
    create array of all the traffic lights
    input:
    amount_road(the amout of possible roads the lights effects)
    black_list(specific trafic lights that we dont need- only singular input\output)
    merged_lights(lights with more than one input\output)
    output: array of all the traffic light in this situation
    """
    RED_LIGHT=0
    counter=0
    all_traffic_Lights=[]
    removed_lights=black_list

    for (inputs,outputs) in merged_lights:
        traffic_light=create_light(counter,inputs,outputs,RED_LIGHT)
        all_traffic_Lights.append(traffic_light)
        counter+=1
        for i in inputs:
            for j in outputs:
                removed_lights.append((i,j))


    for i in range(1,amount_road+1):
        for j in range(1,amount_road+1):
            if (i,j) not in removed_lights:
                all_traffic_Lights.append(create_light(counter,i,j,RED_LIGHT))
                counter+=1
    
            
    return all_traffic_Lights

def create_lanes(amount_lanes:int |None=3):
    """
    create all the needed lanes in a certain road
    input:amount_lanes(how much to create)
    output: array of the lane obj in a certain road
    """
    
    lanes=[]
    for i in range(1,amount_lanes+1):
        lane={}
        lane["lane_index"]=i
        lane["cars_creation"]=random.randint(0,100)
        lanes.append(lane)
    return lanes
        
def create_roads(amount_road:int |None=4):
    """
    create all the roads in a certaion junction
    input:amount_road(how much to create)
    output: array of the road obj in a certain road
    """
    roads=[]
    for i in range(1,amount_road+1):
        road={}
        road["road_index"]=i
        road["num_lanes"]=3#random.randint(1,4)
        road["lanes"]=create_lanes(road["num_lanes"])
        roads.append(road)
    return roads


def create_junction(junction_index:int |None =1):
    """
    create the junction obj
    input:junction_index
    output:junction obj
    """
    juanction={}
    juanction["junction_index"]=junction_index
    juanction["total_roads"]=4#random.randint(1,4)
    juanction["roads"]=create_roads(juanction["total_roads"])
    juanction["traffic_lights"]=create_all_lights(juanction["total_roads"],[(1,2),(2,2)],[([1,2,3],[1,2])])
    return juanction


def create_all_json():
    """
    create all the needed objects and turn them into json
    input: none
    output: all the data for a certain sim in json
    """
    JSON_INDETATION=4
    all_data={}
    all_data["junction"]=create_junction()
    return json.dumps(all_data,indent=JSON_INDETATION)
    

   
def main():
    test=create_all_json()
    with open("sim\creator\example.json","w") as f:
        f.write(test)
    print(test)


if __name__== "__main__":
    main()