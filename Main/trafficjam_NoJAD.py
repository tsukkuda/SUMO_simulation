import traci
import os

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

#ボトルネック区間(大和トンネル)の検知器
DECELERATION_SAG = 0.24

#定数
Td=30
R=50

#減速時の下限速度
# DECELERATION_RATE = 0.9
# DECELERATION_DURATION = 3

#JAD中の減速度
JAD_DECELERATION = 0.3

#sumo-guiの設定ファイル
sumocfg = 'tomei_NoJAD.sumocfg'

#乱数の種
seed = 4
# seed = 23423  # Default

#打ち切りの秒数
stopTime=4000
#データ採取開始時刻
outputStartTime=4000

def main(sumocfg):
    #起動コマンドの設定
    sumoCmd = ['sumo-gui', '-c', sumocfg]

    #オプション
    #乱数の種の設定
    sumoCmd.append('--seed')
    sumoCmd.append(str(seed))
    #起動時にシミュレーションを開始する
    sumoCmd.append('--start')
    sumoCmd.append('True')
    
    #*オプション追加
    #出力先のファイル名 多分xml
    sumoCmd.append('--fcd-output')
    sumoCmd.append('test.xml')
    #出力する属性の指定
    sumoCmd.append('--fcd-output.attributes')
    sumoCmd.append('speed,odometer')

    #GUIの実行
    traci.start(sumoCmd)

    #大和トンネルで減速する車両リスト
    slow_down_yamato = []
    
    #渋滞吸収運転をしている車両リスト
    jad_list = {}

    #削除用のバッファ
    jad_finish_list = []
    
    #自動運転車両
    v_large_list=[]
    
    #*ログ
    speed_log=[]
    
    #csvデータヘッダ
    # print("time,ID,type,value")

    #すべての車両が完走するまで繰り返す
    while traci.simulation.getMinExpectedNumber():
        #シミュレーションステップを1進める
        traci.simulationStep()
        #時間を取得
        time = traci.simulation.getTime()
        
        #設定した時間で打ち切り
        if time>=stopTime:
            break

        #終了地点に到着した車両リストを取得
        arrive_list = traci.simulation.getArrivedIDList()
        remove_list = []

        #各リストから到着した車両を削除する
        for v in arrive_list:
            if v in slow_down_yamato:
                slow_down_yamato.remove(v)
            if v in jad_list.keys():
                remove_list.append(v)

        for v in remove_list:
            del jad_list[v]
            jad_finish_list.remove(v)

        # JADを終了した車両を削除する
        for v, item in jad_list.items():
            if time >= item['decel_step']:
                jad_finish_list.append(v)

        #リストのクリア
        v_large_list=[]
        
        #車両の速度に応じて色を変える
        if time % 1 == 0:
            v_list = traci.vehicle.getIDList()
            for v in v_list:
                speed = traci.vehicle.getSpeed(v)
                if v not in jad_list.keys() or v in jad_finish_list:
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
                        
                
                if "large" in traci.vehicle.getTypeID(v):
                    v_large_list.append(v)

        # #* ここからログ関係
        # if time>outputStartTime:
        #     if time%15==0:
        #         #ログ生成
        #         for v in v_large_list:
        #             speed=traci.vehicle.getSpeed(v)
        #             odo=traci.vehicle.getDistance(v)
        #             start=odo+speed*Td-R
        #             end=odo+speed*Td+R

        #             #範囲に入っている車両の平均速度 
        #             sum=0
        #             count=0
        #             for fv in v_large_list:
        #                 fv_speed=traci.vehicle.getSpeed(fv)
        #                 fv_odo=traci.vehicle.getDistance(fv)
        #                 if start<=fv_odo<=end:
        #                     sum+=1/(3.6*fv_speed)
        #                     count+=1

        #             if count!=0:
        #                 front_ave_speed=count/sum
        #             else:
        #                 #範囲内に車両がいない場合
        #                 front_ave_speed=120

        #             #ログ追加
        #             index=-1
        #             count=0
        #             for diction in speed_log:
        #                 if v==diction["ID"]:
        #                     index=count
        #                     break
        #                 count+=1

        #             if index==-1:
        #                 speed_log.append({"ID":v,"list":[[speed,front_ave_speed/3.6]]})
        #             else:
        #                 if len(speed_log[index]["list"])==17:
        #                     speed_log[index]["list"].pop(0)
        #                 speed_log[index]["list"].append([(speed),front_ave_speed/3.6])

        #             #誤差計算用ログ time,ID,type,speed
        #             print(time,v,0,speed,sep=",")

        #         predict.predict_car_vel(speed_log,time)
        # #* ここまでログ関係

        # サグ部の車両を減速させる
        #4500秒以降はサグ部も減速せずに走行する
        #? 4500s以降でも減速したほうがいいのか?
        if time <= 4500:
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

    traci.close()

if __name__ == "__main__":
    main(sumocfg)