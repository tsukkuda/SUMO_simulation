#必要なもの(ライブラリ)をここで読み込む
import os
import sys
import pathlib
import numpy as np
import tensorflow as tf
from tensorflow.python.keras.models import Sequential,load_model


# 警告を非表示にする
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# このファイルがあるディレクトリの絶対パスを取得
current_dir = pathlib.Path(__file__).resolve().parent
# モジュールのあるパスを追加
sys.path.append(str(current_dir) + '/./')
tf.get_logger().setLevel("ERROR")

# モデルのパスを取得
# model_path = os.getcwd() + "/bestmodel.hdf5"
model_path = os.getcwd() + "/bestmodel_data03.hdf5"
model = load_model(filepath=model_path)

def process_predict(pred_vel_list):
    pred_speed = model.predict(pred_vel_list)
    return pred_speed

def predict_car_vel(speed_log,time):
    '''
    車両の速度を予測する
    '''
    WindowSize = 15 #入力データのウィンドウサイズ
    MedianSize = 3  #移動平均を取る大きさ

    #移動平均用のマージンを確保して配列を作成
    ### n=1
    input_data = np.empty((0,WindowSize+MedianSize-1,2))

    # for type0_car in self.type0_list:
    #     if len(type0_car.vel_list) < WindowSize+MedianSize-1:
    #         continue

    #     #NOTE shape(1,15,2)の形のndarrayを作成する
    #     tmp_data = np.array([[[car_vel, front_vel] for car_vel, front_vel in zip(type0_car.vel_list[-(WindowSize+MedianSize-1):], type0_car.avr_front_vel[0][-(WindowSize+MedianSize-1):])]])
    #     input_data = np.append(input_data, tmp_data, axis=0)
    
    for log in speed_log:
        if len(log["list"]) < WindowSize+MedianSize-1:
            continue
        
        #NOTE shape(1,15,2)の形のndarrayを作成する
        tmp_data=np.array([log["list"][-17:]])
        input_data = np.append(input_data, tmp_data, axis=0)

    if input_data.size == 0:
        return

    # max_vel = max(self.vel_hope_max)/3.6 #simで取り得る最大速度(速度予測プログラムの正規化でも同値を必ず使用すべし)【鉢嶺】
    max_vel = 120/3.6
    input_data = np.true_divide(input_data.astype(np.float),max_vel)#配列のdtypeが'O'だったので'float'に変換

    #NOTE 福丸: process_predictに入力し速度を予測する
    predVel = process_predict([input_data])
    # predVel = process_predict([input_data/max_vel])

    # i = 0
    # for type0_car in self.type0_list:
    #     if len(type0_car.vel_list) < WindowSize+MedianSize-1:
    #         continue

    #     type0_car.pred_vel = predVel[i][0] * max_vel#正規化を戻す
    #     i += 1
    i=0
    for log in speed_log:
        if len(log["list"]) < WindowSize+MedianSize-1:
            continue
    
        predSpeed = predVel[i][0] * max_vel#正規化を戻す
        print(time,log["vehicle_ID"],1,predSpeed,sep=",")
        i+=1
    
    

if __name__ == "__main__":
    pred_vel_list = np.load("np_testdata.npy")
    predvel = process_predict(pred_vel_list[0])
    print(predvel)