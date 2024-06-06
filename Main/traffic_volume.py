import traci
import os
import csv
import pandas as pd

def traffic_volume(DETECTOR0,DETECTOR1,vPre_list):
    v_list=[]
    flow_in_list=[]
    
    flow_in_density=0  #k_in
    flow_in_speed=0    #v_in
    
    v_list+=traci.lanearea.getLastStepVehicleIDs(DETECTOR0)
    v_list+=traci.lanearea.getLastStepVehicleIDs(DETECTOR1)
        
    #流入車両の取得
    #1step前のリストと比べて，新しく現れた車両を流入(in)とする
    for v in v_list:
        if v not in vPre_list:
            flow_in_list.append(v)
        
    pos_max=0  #k_inを求めるため
    sum=0       #v_inを求めるため
        
    #流入車両があったら計算
    if len(flow_in_list)!=0:
        for v in flow_in_list:
            pos_max = max(traci.vehicle.getLanePosition(v), pos_max)
            sum+=1/(3.6*traci.vehicle.getSpeed(v))
            
        #k_in算出
        flow_in_density=len(flow_in_list)/((3204.87-pos_max)*2/1000)
        #v_in算出
        flow_in_speed=len(flow_in_list)/sum
    
    #1step前の車両リスト更新
    vPre_list=[]
    vPre_list+=traci.lanearea.getLastStepVehicleIDs(DETECTOR0)
    vPre_list+=traci.lanearea.getLastStepVehicleIDs(DETECTOR1)
    
    return flow_in_density,flow_in_speed,vPre_list

if __name__ == "__main__":
    print("This file is used only as modlue.")