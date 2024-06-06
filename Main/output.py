import csv
import pandas as pd

#csv出力で使いそうなもの
columns=["time","id","pos","vel","accl"]
with open('vehicle_log.csv', 'w',newline="") as f:
    writer = csv.writer(f)
    writer.writerow(columns)
f.close()

with open('vehicle_log.csv', 'a',newline="") as f:
    writer = csv.writer(f)
    list_append = [time,v,traci.vehicle.getPosition(v),traci.vehicle.getSpeed(v),traci.vehicle.getAccel(v)]
    writer.writerow(list_append)
f.close()