import traci
import os
import csv
import pandas as pd

import traffic_volume
from readdata import generate_car_info
# import predict

#ボトルネック区間(大和トンネル)のEdgeID
# YAMATO_TN = '31887784'
# UPSIDE_YAMATO = '285190605'

#ループコイルのID
# INDUCTION_LOOP0 = 'e1_0'
# INDUCTION_LOOP1 = 'e1_1'

#速度制御区間の検知器
LANE_AREA_DETECTOR0 = 'e2_0'
LANE_AREA_DETECTOR1 = 'e2_1'

LANE_AREA_DETECTOR2 = 'e2_2'
LANE_AREA_DETECTOR3 = 'e2_3'

LANE_AREA_DETECTOR4 = 'e2_4'
LANE_AREA_DETECTOR5 = 'e2_5'

#ボトルネック区間(大和トンネル)の検知器
YAMATO_DETECTOR0 = 'y_0'
YAMATO_DETECTOR1 = 'y_1'

#速度観測区間の検知器
IFOY_DETECTOR_a0 = 'x_a0'
IFOY_DETECTOR_a1 = 'x_a1'

IFOY_DETECTOR_b0 = 'x_b0'
IFOY_DETECTOR_b1 = 'x_b1'

IFOY_DETECTOR_c0 = 'x_c0'
IFOY_DETECTOR_c1 = 'x_c1'

#定数
Td=30
R=100

#サグ部の減速度
DECELERATION_SAG = 0.24

#減速時の下限速度
# DECELERATION_RATE = 0.9
# DECELERATION_DURATION = 3

#JAD中の減速度
JAD_DECELERATION = 0.3

#sumo-guiの設定ファイル
sumocfg = 'tomei_JAD.sumocfg'

#乱数の種
seed = 4
# seed = 23423  # Default

def main(sumocfg):
        
    #my ここからcsv読み込んで車両リスト作成
    generate_car_info([0,1],"data_2021-10-06-1500.csv") #data_日付-1500.csv
    #my ここまでcsv読み込んで車両リスト作成
    
    #起動コマンドの設定
    sumoCmd = ['sumo', '-c', sumocfg]
    #sumoCmd = ['sumo', '-c', sumocfg] GUIなし
    #sumoCmd = ['sumo-gui', '-c', sumocfg] GUI

    #オプション
    #乱数の種の設定
    sumoCmd.append('--seed')
    sumoCmd.append(str(seed))
    #起動時にシミュレーションを開始する
    sumoCmd.append('--start')
    sumoCmd.append('True')

    #GUIの実行
    traci.start(sumoCmd)

    #大和トンネルで減速する車両リスト
    slow_down_yamato = []
    
    #渋滞吸収運転をしている車両リスト
    jad_list = {}
    #削除用のバッファ
    remove_list = []
    
    #1step前の車両リスト
    vPre_a_list=[]
    vPre_b_list=[]
    vPre_c_list=[]
    vPre_e2_01_list=[]
    vPre_e2_23_list=[]
    vPre_e2_45_list=[]
    vPre_yamato_list=[]
    
    #ログ
    speed_log=[]
    
    #csv生データ出力用ヘッダ
    print("time,vehicle_ID,position,car_speed")


    #すべての車両が完走するまで繰り返す
    while traci.simulation.getMinExpectedNumber():
        #シミュレーションステップを1進める
        traci.simulationStep()
        #時間を取得
        time = traci.simulation.getTime()
        
        #[] ここで時間になったら車両生成する いろいろ生成条件があるみたい road.py参照
        # traci.vehicle.add(vehID=str(vehicleID),  # 車両ID
        #                           typeID="passenger",  # 車両タイプ
        #                           routeID="r_main",  # ルートID
        #                           departLane=str(lane_index),  # 出発レーン
        #                           departSpeed="last",  # 出発時の速度
        #                           arrivalLane="current",  # 到着レーン
        #                           depart=time)  # 出発時刻
        
        #6000sで打ち切り
        if time>5000:
            break
        
        #終了地点に到着した車両リストを取得
        arrive_list = traci.simulation.getArrivedIDList()
        

        #各リストから到着した車両を削除する
        for v in arrive_list:
            if v in slow_down_yamato:
                slow_down_yamato.remove(v)
            if v in jad_list.keys():
                remove_list.append(v)
                


        #車両の速度に応じて色を変える
        if time % 1 == 0:
            v_list = traci.vehicle.getIDList()
            for v in v_list:
                speed = traci.vehicle.getSpeed(v)

                #減速制御中の車両は別の色をつける
                if v in jad_list.keys():
                    traci.vehicle.setColor(v, (236, 0, 140, 255))
                else :
                    if   speed < 5.56:
                        traci.vehicle.setColor(v, (255, 0, 0, 255))
                    elif speed < 11.11:
                        traci.vehicle.setColor(v, (255, 63, 0, 255))
                    elif speed < 16.67:
                        traci.vehicle.setColor(v, (255, 127, 0, 255))
                    elif speed < 22.22:
                        traci.vehicle.setColor(v, (255, 255, 0, 255))
                    elif speed < 27.78:
                        traci.vehicle.setColor(v, (0, 255, 0, 255))
                    else:
                        traci.vehicle.setColor(v, (0, 255, 255, 255))
                        
                #csv生データ出力用
                if "large" in traci.vehicle.getTypeID(v):
                    print(time,v,traci.vehicle.getDistance(v),traci.vehicle.getSpeed(v),sep=",")

        # サグ部の車両を減速させる
        #4500秒以降はサグ部も減速せずに走行する
        #トンネル内の予測平均速度でやるのがいいかも
        if time <= 4000:
            #検知器の上にいた車両（サグ部を走行している車両）を取得する
            v_list = []
            v_list += traci.lanearea.getLastStepVehicleIDs(YAMATO_DETECTOR0)
            v_list += traci.lanearea.getLastStepVehicleIDs(YAMATO_DETECTOR1)

            
            for v in v_list:    
                #既に減速の設定済みの車両はスキップ
                if v in slow_down_yamato:
                    continue

                #車両タイプを取得
                vehicle_type = traci.vehicle.getTypeID(v)
                #一般車両の一部をサグ部で減速させる
                if "standard1" in vehicle_type or "standard2" in vehicle_type or "standard3" in vehicle_type:
                    speed = traci.vehicle.getSpeed(v)
                    decelerated_speed = speed - 15/3.6
                    if decelerated_speed < 50/3.6:
                        decelerated_speed = 50/3.6

                    duration = (speed - decelerated_speed) / DECELERATION_SAG
                    if duration > 0:
                        traci.vehicle.slowDown(
                            v,
                            decelerated_speed,
                            duration
                            )
                        slow_down_yamato.append(v)
                        # print('slow down : ', v, ' , target_vel : ', decelerated_speed, ' , duration : ', duration)

        
        #交通量
        kin_a,vin_a,vPre_a_list=traffic_volume.traffic_volume(IFOY_DETECTOR_a0,IFOY_DETECTOR_a1,vPre_a_list)
        # print(time, "x_a01", kin_a, vin_a, sep=",")
        
        kin_yamato,vin_yamato,vPre_yamato_list=traffic_volume.traffic_volume(YAMATO_DETECTOR0,YAMATO_DETECTOR1,vPre_yamato_list)
        # print(time, "yamato", kin_yamato, vin_yamato, sep=",")
        
        kin_e2_01,vin_e2_01,vPre_e2_01_list=traffic_volume.traffic_volume(LANE_AREA_DETECTOR0,LANE_AREA_DETECTOR1,vPre_e2_01_list)
        # print(time, "e2_01", kin_e2_01, vin_e2_01, sep=",")
        
        kin_e2_23,vin_e2_23,vPre_e2_23_list=traffic_volume.traffic_volume(LANE_AREA_DETECTOR2,LANE_AREA_DETECTOR3,vPre_e2_23_list)
        # print(time, "e2_23", kin_e2_23, vin_e2_23, sep=",")
        
        
        #目標速度
        if kin_e2_01!=0 and kin_e2_23!=0:
            v_tar=kin_yamato*vin_yamato/kin_e2_01
        else:
            v_tar=max(vin_e2_01-10,70)
        # print(v_tar)
        
        
        
        # #走行距離と速度取得
        # v_list = traci.vehicle.getIDList()
        # v_large_list=[]
        
        # #自動運転車両のみ抜き出す
        # for v in v_list:
        #     if "large" in traci.vehicle.getTypeID(v):
        #         v_large_list.append(v)
        
        # if time%5==0:
        #     #ログ生成
        #     for v in v_large_list:
        #         speed=traci.vehicle.getSpeed(v)
        #         odo=traci.vehicle.getDistance(v)
        #         start=odo+speed*Td-R
        #         end=odo+speed*Td+R
                
        #         #範囲に入っている車両の平均速度 
        #         sum=0
        #         count=0
        #         for fv in v_large_list:
        #             fv_speed=traci.vehicle.getSpeed(fv)
        #             fv_odo=traci.vehicle.getDistance(fv)
        #             if start<=fv_odo<=end:
        #                 sum+=1/(3.6*fv_speed)
        #                 count+=1

        #         if count!=0:
        #             front_ave_speed=count/sum
        #         else:
        #             #範囲内に車両がいない場合
        #             front_ave_speed=120
                
        #         #ログ追加
        #         index=-1
        #         count=0
        #         for diction in speed_log:
        #             if v==diction["vehicle_ID"]:
        #                 index=count
        #                 break
        #             count+=1
                
        #         if index==-1:
        #             speed_log.append({"vehicle_ID":v,"list":[[speed,front_ave_speed/3.6]]})
        #         else:
        #             if len(speed_log[index]["list"])==17:
        #                 speed_log[index]["list"].pop(0)
        #             speed_log[index]["list"].append([(speed),front_ave_speed/3.6])
                    
        #         #誤差計算用ログ
        #         print(time,v,0,speed,sep=",")
                
        #     predict.predict_car_vel(speed_log,time)

        
        # 減速制御をする車両リストの初期化
        v_list = []

        if 0<traci.lanearea.getIntervalMeanSpeed(YAMATO_DETECTOR0)<70/3.6:
            v_list += traci.lanearea.getLastStepVehicleIDs(LANE_AREA_DETECTOR2)
            if traci.lanearea.getIntervalMeanSpeed(YAMATO_DETECTOR0)<65/3.6:
                v_list += traci.lanearea.getLastStepVehicleIDs(LANE_AREA_DETECTOR4)
                
        if 0<traci.lanearea.getIntervalMeanSpeed(YAMATO_DETECTOR1)<70/3.6:
            v_list += traci.lanearea.getLastStepVehicleIDs(LANE_AREA_DETECTOR3)
            if traci.lanearea.getIntervalMeanSpeed(YAMATO_DETECTOR1)<65/3.6:
                v_list += traci.lanearea.getLastStepVehicleIDs(LANE_AREA_DETECTOR5)

        

        for v in v_list:
            # 車両の情報を取得
            vehicle_type = traci.vehicle.getTypeID(v)
            speed = traci.vehicle.getSpeed(v)
            accl = traci.vehicle.getAcceleration(v)

            if v in jad_list.keys():
                #目標速度まで減速した車両の加速度を0に設定する
                if accl > 0:
                    traci.vehicle.setAcceleration(v, 0.0, 1.0)
                continue

            # 大型車を減速させる
            if speed > v_tar/3.6 and "large" in vehicle_type:
                decelerated_speed = v_tar/3.6
                duration = (speed - decelerated_speed) / JAD_DECELERATION

                traci.vehicle.slowDown(
                    v,
                    decelerated_speed,
                    duration
                    )

                # JAD制御情報を記録する
                jad_list[v] = dict(decel_step=int(time+duration), keep_step=-1)
                # print('jad : ', v, ' , target_vel : ', decelerated_speed, ' , duration : ', duration)

        # エリアを抜けた車両をJAD制御車両リストから削除する
        for v in jad_list.keys():
            if v not in v_list:
                remove_list.append(v)

        for v in remove_list:
            del jad_list[v]
        
        # リストの初期化
        remove_list = []

    # f.close()
    traci.close()

if __name__ == "__main__":
    main(sumocfg)