import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
import seaborn as sns
from function import *


if __name__ == "__main__":

    plot = "TimeToTarget"
    mazes_names = ["ToyMazeTest", "SmallMazeTest", "MediumMazeTest","BigMazeTest"]
    difficulties = ["Close","Medium","Far"]

    #create a list with maze+target names that will represent the x-axis
    x_ticks = [name + difficulty for name in mazes_names for difficulty in difficulties] 

    time_values, models = get_time_values(mazes_names, plot)
    print(np.array(time_values).shape)
    df = pd.DataFrame(np.array(time_values).T, columns=models,index=x_ticks) 
    # dataframe with models as columns and targets as rows

    swarms_sizes = [16,20]
    # swarms_sizes = [16,20]

    fig, axs = plt.subplots(1,len(swarms_sizes))

    
    
    for i, swarm in enumerate(swarms_sizes):

        #select models that you want to plot.

        # [c for c in df.columns if c.startswith(str(swarm))]  --> all models
        # [c for c in df.columns if c.startswith(str(swarm)) and ("NoComm" in c or "Free" in c) and "Zeroed" not in c and "Disturbed" not in c and "Distance" not in c] ->
                        #m compare no comm and free
        # [c for c in df.columns if c.startswith(str(swarm)) and ("Free" in c or "Zeroed" not in c or "Disturbed" not in c) and "NoComm" in c and "Distance" not in c]


        columns = [c for c in df.columns if c.startswith(str(swarm)) ]
        

        
        # you can play with iloc to plot just some rows. [len(swarm) - 6:] is getting only last 6 rows (correspond to medium and big maze)
        # df_swarm = df[columns]
        df_swarm = df[columns].iloc[len(df) - 6:]      
        
        df_swarm.plot.bar(rot=45, ax = axs[i], legend = False)
        axs[i].set_xticklabels(axs[i].get_xticklabels(),rotation=45,size="xx-small")
        axs[i].set_title(str(swarm) + " Agents")

        if i==0:
            axs[i].set_ylabel("Time to Target") 


    fig.legend([c[2:] for c in columns])
    plt.show()

    #----------------------------
    # plot = "ExplorationRate"
    # mazes_names = ["ToyMazeTest", "SmallMazeTest", "MediumMazeTest","BigMazeTest"]
    # difficulties = ["Close","Medium","Far"]

    # #create a list with maze+target names that will represent the x-axis
    # x_ticks = [name + difficulty for name in mazes_names for difficulty in difficulties] 

    # time_values, models = get_time_values(mazes_names, plot)
    # print(np.array(time_values).shape)
    # df = pd.DataFrame(np.array(time_values).T, columns=models,index=x_ticks) 
    # # dataframe with models as columns and targets as rows

    # swarms_sizes = [4,8,12,16,20]
    # # swarms_sizes = [16,20]

    # fig, axs = plt.subplots(1,len(swarms_sizes))

    
    
    # for i, swarm in enumerate(swarms_sizes):

    #     #select models that you want to plot.

    #     # [c for c in df.columns if c.startswith(str(swarm))]  --> all models
    #     # [c for c in df.columns if c.startswith(str(swarm)) and ("NoComm" in c or "Free" in c) and "Zeroed" not in c and "Disturbed" not in c and "Distance" not in c] ->
    #                     #m compare no comm and free
    #     # [c for c in df.columns if c.startswith(str(swarm)) and ("Free" in c or "Zeroed" not in c or "Disturbed" not in c) and "NoComm" in c and "Distance" not in c]


    #     columns = [c for c in df.columns if c.startswith(str(swarm)) and ("NoComm" in c or "Target" ) and "Distance" not in c and "Position" not in c and "Free" not in c]
        

        
    #     # you can play with iloc to plot just some rows. [len(swarm) - 6:] is getting only last 6 rows (correspond to medium and big maze)
    #     # df_swarm = df[columns]
    #     df_swarm = df[columns].iloc[len(df) - 6:]      
        
    #     df_swarm.plot.bar(rot=45, ax = axs[i], legend = False)
    #     axs[i].set_xticklabels(axs[i].get_xticklabels(),rotation=45,size="xx-small")
    #     axs[i].set_title(str(swarm) + " Agents")

    #     if i==0:
    #         axs[i].set_ylabel("Time to Target") 


    # fig.legend([c[2:] for c in columns])
    # plt.show()



