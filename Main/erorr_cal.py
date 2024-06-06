import pandas as pd
import math

#step*5秒毎のRMSRE(平均平方二乗誤差率)を求める
step=500

#RMSPEを格納するDataFrame
rmspe_df=pd.DataFrame()

#rmspe_dfに追加する際のやつ
add_dict={}

#csv読み込み
base_df=pd.read_csv("./record_5.csv",encoding="utf-16")

#vehicle_IDで分ける(車両ごとにspeed_logを分割)
veh_group=base_df.groupby("vehicle_ID")

#各車両毎のRMSREを計算
for vehicle_ID,group_df in base_df.groupby("vehicle_ID"):
    if group_df.query("type ==1").empty:
        add_df=pd.DataFrame({},index=[vehicle_ID])
        continue
    
    add_dict.clear()

    #result
    result_base_df=group_df.groupby("type").get_group(0)
    #warning対策，timeをindexに指定する
    result_df=(result_base_df.copy()).set_index("time")
    #mergeするためcolumns名を変える
    result_df.drop(columns=["vehicle_ID","type"],inplace=True)
    result_df.rename(columns={"value":"result"},inplace=True)

    #predict
    #warning対策
    predict_base_df=(group_df.groupby("type").get_group(1)).copy()
    #30s後のresultと比較するため
    predict_base_df.loc[:,("time")]+=30
    predict_base_df["value"].mask(predict_base_df["value"]<0,0,inplace=True)
    #warning対策，timeをindex
    predict_df=(predict_base_df.copy()).set_index("time")
    #mergeするためcolumns名を変える
    predict_df.drop(columns=["vehicle_ID","type"],inplace=True)
    predict_df.rename(columns={"value":"predict"},inplace=True)


    #merge(実際の値と予測値を並べたデータ)
    merged_df=pd.merge(result_df,predict_df,left_index=True,right_index=True)
    merged_df["squared"]=((merged_df["result"]-merged_df["predict"])/merged_df["result"])**2
    # ただの単純差分の平均を求める場合
    # merged_df["squared"]=(merged_df["result"]-merged_df["predict"])

    sliced_dfs = [merged_df.iloc[i:i+step,:] for i in range(0, len(merged_df), step)]
    i=0
    for df_i in sliced_dfs:
        key=str(i*step*5)+"s-"+str((i+1)*step*5)+"s"
        add_dict[key]=[math.sqrt(df_i["squared"].mean())]
        #ただの単純差分の平均を求める場合
        # add_dict[key]=[df_i["squared"].mean()]
        i+=1
        
    #辞書型からdataframeに変換して，それをrmspe_dfへ追加
    add_df=pd.DataFrame(add_dict,index=[vehicle_ID])
    rmspe_df=pd.concat([rmspe_df,add_df])
    
#計算結果をcsvで出力
rmspe_df.to_csv("./rmcre_5.csv")




# #rmspe_dfに追加する際のやつ
# add_dict={}

# test_df=veh_group.get_group("flow17largelane1.99")

# #result
# result_base_df=test_df.groupby("type").get_group(0)
# #warning対策，timeをindex
# result_df=(result_base_df.copy()).set_index("time")
# result_df.drop(columns=["vehicle_ID","type"],inplace=True)
# result_df.rename(columns={"value":"result"},inplace=True)

# #predict
# #warning対策
# predict_base_df=(test_df.groupby("type").get_group(1)).copy()
# #30s後のresultと比較するため
# predict_base_df.loc[:,("time")]+=30
# #warning対策，timeをindex
# predict_df=(predict_base_df.copy()).set_index("time")
# predict_df.drop(columns=["vehicle_ID","type"],inplace=True)
# predict_df.rename(columns={"value":"predict"},inplace=True)


# #merge
# merged_df=pd.merge(result_df,predict_df,left_index=True,right_index=True)
# merged_df["squared"]=((merged_df["predict"]-merged_df["result"])/merged_df["result"])**2

# sliced_dfs = [merged_df.iloc[i:i+step,:] for i in range(0, len(merged_df), step)]
# i=0
# for df_i in sliced_dfs:
#     key=str(i*step*5)+"s-"+str((i+1)*step*5)+"s"
#     add_dict[key]=[math.sqrt(df_i["squared"].mean())]
#     i+=1

# add_df=pd.DataFrame(add_dict,index=["flow17largelane1.99"])
# rmspe_df=pd.concat([rmspe_df,add_df])
# print(rmspe_df)