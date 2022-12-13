import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
import seaborn as sns
from function import *
from scipy.stats import ttest_rel


if __name__ == "__main__":

    plot = "TimeToTarget"
    mazes_names = ["ToyMazeTest", "SmallMazeTest", "MediumMazeTest","BigMazeTest"]
    difficulties = ["Close","Medium","Far"]

    #create a list with maze+target names that will represent the x-axis
    n_tests = [3,6,18,30]

    #create a list with maze+target names that will represent the x-axis
    x_ticks = [name + str(n+1)  for name,n_test in zip(mazes_names,n_tests) for n in range(n_test) ] 

    time_values, models = get_time_values(mazes_names, plot)
    print(np.array(time_values).shape)
    df = pd.DataFrame(np.array(time_values).T, columns=models,index=x_ticks) 
    # dataframe with models as columns and targets as rows

    swarms_sizes = [4,8,12,16,20]
    # swarms_sizes = [16,20]

    


    columns = parse_columns(columns=df.columns, to_include = ["Free", "Zeroed", "Disturbed", "Random", "NoComm","Inside"], to_not_include= [ "Distance", ])
    
    print(columns)
    

    dict = {"average_Free" : df[[c for c in columns if "Disturbed" not in c and "Inside" not in c and "Zeroed" not in c and "NoComm" not in c and "Random" not in c]].mean(axis=1), 
    "average_Zeroed" : df[[c for c in columns if "Zeroed" in c]].mean(axis=1), 
    "average_Disturbed" : df[[c for c in columns if "Disturbed" in c]].mean(axis=1),
    "average_NoComm" : df[[c for c in columns if "NoComm" in c]].mean(axis=1),
    "average_Inside" : df[[c for c in columns if "Inside" in c]].mean(axis=1),
    "average_Random" : df[[c for c in columns if "Random" in c]].mean(axis=1)}
        
    df_to_plot = pd.DataFrame()
    
    for a in dict:
        df_to_plot[a] = dict[a]

    df_to_plot
    print(df_to_plot)

    print("T_TEST free - random: " , ttest_rel(df_to_plot["average_Random"], df_to_plot["average_Free"]))
    print("T_TEST disturbed - random: " , ttest_rel(df_to_plot["average_Random"], df_to_plot["average_Disturbed"]))
    print("T_TEST free - disturbed: " , ttest_rel(df_to_plot["average_Disturbed"], df_to_plot["average_Free"]))
    print("T_TEST free - noComm: " , ttest_rel(df_to_plot["average_NoComm"], df_to_plot["average_Free"]))
    print("T_TEST randominside - free: " , ttest_rel(df_to_plot["average_Inside"], df_to_plot["average_Free"]))
    
    # df_to_plot.mean().plot.bar(rot=45, legend = False)
    sns.boxplot(df_to_plot)

    
    fig, axs = plt.subplots(1,len(swarms_sizes))
    for i, swarm in enumerate(swarms_sizes):

        #select models that you want to plot.

        # [c for c in df.columns if c.startswith(str(swarm))]  --> all models
        # [c for c in df.columns if c.startswith(str(swarm)) and ("NoComm" in c or "Free" in c) and "Zeroed" not in c and "Disturbed" not in c and "Distance" not in c] ->
                        #m compare no comm and free
        # [c for c in df.columns if c.startswith(str(swarm)) and ("Free" in c or "Zeroed" not in c or "Disturbed" not in c) and "NoComm" in c and "Distance" not in c]


        

        columns_swarm = [c for c in columns if c.startswith(str(swarm))]
        # colors = []
        
        
        # you can play with iloc to plot just some rows. [len(swarm) - 6:] is getting only last 6 rows (correspond to medium and big maze)
        # df_swarm = df[columns]
        df_swarm = df[columns_swarm].mean()      
        
        df_swarm.plot.bar(rot=45, ax = axs[i], legend = False)
        axs[i].set_xticklabels(axs[i].get_xticklabels(),rotation=45,size="xx-small")
        axs[i].set_title(str(swarm) + " Agents")

        if i==0:
            axs[i].set_ylabel("Time to Target") 


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



