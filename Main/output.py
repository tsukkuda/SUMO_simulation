import csv
import os


def outputData(foldername,filename,header,data):
    #出力フォルダのパス
    folderpath="./"+foldername
    #ディレクトリ作成
    os.makedirs(folderpath,exist_ok=True)
    
    #出力ファイルのパス
    filepath=folderpath+"/"+filename
    

    print(filename)
    print("===データ出力中===")
    
    with open(filepath,mode="w",newline='') as f:
        writer = csv.writer(f)
        
        #ヘッダー作成
        writer.writerow(header)
        #データを書き込む
        writer.writerows(data)
    
    print("===データ出力完了===")
