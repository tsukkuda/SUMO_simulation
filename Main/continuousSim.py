import traci
import os
import random

import trafficjam_NoJAD


# シミュレーション回数
num_simulations = 10

if __name__ == "__main__":
    for i in range(num_simulations):
        print()
        print("===sim:",i," START===")
        
        # 各シミュレーションで異なるseed設定）
        seed=random.randint(0,10000)
        #sim実行
        trafficjam_NoJAD.main(trafficjam_NoJAD.sumocfg,seed)
        
        print("===sim:",i," FINISH===")
        print()
    print("All sim done. thx for waiting!")