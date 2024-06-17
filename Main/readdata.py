import numpy as np
import csv

#my レーン毎に車両の情報をリストに格納
def generate_car_info(queue,RealData_name): #? queueはlaneのタプルっぽい

    gen_timetable = [[] for i in queue]
    gen_typelist = [[] for i in queue]
    gen_init_vel_list = [[] for i in queue]
    gen_ss_list = [[] for i in queue]

    timetable = [[] for i in queue]
    typelist = [[] for i in queue]
    init_vel_list = [[] for i in queue]
    ss_list = [[] for i in queue]

    #csv_file = open("RealData/data.csv", "r")
    csv_file = open("RealData/"+RealData_name, "r")
    f = csv.reader(csv_file)
    for row in f:
        time     = int(float(row[1]))
        type     = int(row[2])
        init_vel = float(row[3]) / 3.6
        ss       = float(row[4])
        lane     = int(row[7])-1
        timetable[lane].append(time)
        typelist[lane].append(type)
        init_vel_list[lane].append(init_vel)
        ss_list[lane].append(ss)
    csv_file.close()

    for lane in range(len(queue)):
        gen_timetable[lane] = dict(timetable = timetable[lane], next = 0)
        gen_typelist[lane] = dict(type = typelist[lane], next = 0)
        gen_init_vel_list[lane] = dict(init_vel = init_vel_list[lane], next = 0)
        gen_ss_list[lane] = dict(timetable = ss_list[lane], next = 0)
        
    return [gen_timetable, gen_typelist, gen_init_vel_list, gen_ss_list]