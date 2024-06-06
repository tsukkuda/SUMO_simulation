import traci
import os
import csv
import pandas as pd
import numpy as np

#type=0ならば予測, type=1ならば結果
record_df=pd.DataFrame(columns=["time","vehicle_ID","type","value"])

def record(time,vehicle_ID,type,value):
    global record_df
    add_df=pd.DataFrame({"time":[time],"vehicle_ID":[vehicle_ID],"type":[type],"value":[value]},)
    record_df=pd.concat([record_df,add_df],ignore_index=True)
    

def output():
    record_df.to_csv("./data_output/record.csv",index=False)
    print("csv file export is complete.")

if __name__ == "__main__":
    print("This file is used only as modlue.")
    
    # #以下動作確認用
    # print(record_df)
    # record(123,"vah17",0,55)
    # record(123,"vah20",0,60)
    # record(125,"vah17",0,58)
    # record(127,"vah20",1,120)
    # print(record_df)
    # output()