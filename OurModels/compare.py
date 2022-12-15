import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
import seaborn as sns
from function import *
from scipy.stats import ttest_rel

plt.style.use("ggplot")

if __name__ == "__main__":

    plot = "TimeToTarget"
    mazes_names = ["ToyMazeTest", "SmallMazeTest", "MediumMazeTest","BigMazeTest"]
    difficulties = ["Close","Medium","Far"]

    #create a list with maze+target names that will represent the x-axis
    n_tests = [3,6,18,30]

    #create a list with maze+target names that will represent the x-axis
    x_ticks = [name + str(n+1)  for name,n_test in zip(mazes_names,n_tests) for n in range(n_test) ] 

    time_values, models = get_time_values(mazes_names, plot)
    df = pd.DataFrame(np.array(time_values).T, columns=models,index=x_ticks) 
    # dataframe with models as columns and targets as rows

   
    # swarms_sizes = [16,20]

    df_average = pd.DataFrame()
    df_average["Free"] = pd.concat([df["4AgentsFree"], df["8AgentsFree"], df["12AgentsFree"],df["16AgentsFree"],df["20AgentsFree"]])
    df_average["NoCommunication"] = pd.concat([df["4AgentsNoComm"], df["8AgentsNoComm"], df["12AgentsNoComm"],df["16AgentsNoComm"],df["20AgentsNoComm"]])
    df_average["DistanceFree"] = pd.concat([df["4AgentsDistanceFree"], df["8AgentsDistanceFree"], df["12AgentsDistanceFree"],df["16AgentsFree"],df["20AgentsDistanceFree"]])
    df_average["Distance"] = pd.concat([df["4AgentsDistance"], df["8AgentsDistance"], df["12AgentsDistance"],df["16AgentsDistance"],df["20AgentsDistance"]])
    

    

    
    df_free = pd.DataFrame()

    df_free["Free"] = pd.concat([df["4AgentsFree"], df["8AgentsFree"], df["12AgentsFree"],df["16AgentsFree"],df["20AgentsFree"]])
    df_free["FreeDisturbed"] = pd.concat([df["4AgentsFreeDisturbed"], df["8AgentsFreeDisturbed"], df["12AgentsFreeDisturbed"],df["16AgentsFreeDisturbed"],df["20AgentsFreeDisturbed"]])
    df_free["FreeRandom"] = pd.concat([df["4AgentsFreeRandom"], df["8AgentsFreeRandom"], df["12AgentsFreeRandom"],df["16AgentsFreeRandom"],df["20AgentsFreeRandom"]])    
    df_free["FreeZeroed"] = pd.concat([df["4AgentsFreeZeroed"], df["8AgentsFreeZeroed"], df["12AgentsFreeZeroed"],df["16AgentsFreeZeroed"],df["20AgentsFreeZeroed"]])    

    sns.boxplot(df_free)
    plt.ylabel("Time to target")
    plt.figure()
    # columns = col
    # print(columns)

    # dct = {
    # "FreeCommunication" : df[[c for c in columns if "Free" in c and "Distance" not in c]].mean(axis=1), 
    # # "average_Zeroed" : df[[c for c in columns if "Zeroed" in c]].mean(axis=1), 
    # # "average_Disturbed" : df[[c for c in columns if "Disturbed" in c]].mean(axis=1),
    # "NoCommunication" : df[[c for c in columns if "NoComm" in c]].mean(axis=1),
    # "DistanceCommunication" : df[[c for c in columns if "Distance" in c and "Free" not in c]].mean(axis=1),
    # "DistanceFreeCommunication" : df[[c for c in columns if "Distance" in c and "Free" in c]].mean(axis=1),
    # # "average_Inside" : df[[c for c in columns if "Inside" in c]].mean(axis=1),
    # # "average_Random" : df[[c for c in columns if "Random" in c]].mean(axis=1)
    # }
        
    # df_average = pd.DataFrame()
    
    # for a in dct:
    #     df_average[a] = dct[a]

    # print(df_average)

    # df = df.iloc[-30:,:]
    # print(df)


    # # df_count = df[df==300.0].count()

    # df_count = df[columns].apply(pd.Series.value_counts).iloc[-1]

    # d = {
    #     "Free" : 0,
    #     "Distance":0,
    #     "DistanceFree":0,
    #     "NoCommunication":0
    # }

    # print(df_count)

    # for c in df_count.index:
    #     # if c.startswith("20"):
    #         if "Free" in c and "Distance" not in c:
    #             d["Free"] += df_count.loc[c]

    #         if "Distance" in c and "Free" not in c:
    #             d["Distance"] += df_count.loc[c]

    #         if "Distance" in c and "Free" in c:
    #             d["DistanceFree"] += df_count.loc[c]

    #         if "NoComm" in c:
    #             d["NoCommunication"] += df_count.loc[c]

    # for k in d:
    #     d[k] *= 100 / len(df) / 5
    #     d[k] = round(d[k],2)

    # ax = plt.bar(*zip(*d.items()))
    # plt.bar_label(ax)

    # plt.title("Unfound targets by each model type.")
    # plt.xlabel("Model")
    # plt.ylabel("Percentage of unfound targets")

    df_average = df_average[-30:]
    print(df_average)


    df_count = df_average[df_average == 300.0].count()
    print(df_count)

    d = df_count.to_dict()
    for k in d:
        d[k] *= 100 / len(df_average)
        d[k] = round(d[k],2)


    print("------------------------")
    print(d)
    print("------------------------")

    ax = plt.bar(*zip(*d.items()))
    plt.bar_label(ax)
    plt.ylabel("Percentage of unfound targets")

    #----------------------------------

    

    plt.figure()
    c = df_average.columns.tolist()
    c.sort(key=lambda x:df_average[x].median(), reverse=True)
    df_to_plot = df_average[c]

    time_values, models = get_time_values(mazes_names, "ExplorationRate")
    df_explo = pd.DataFrame(np.array(time_values).T, columns=models,index=x_ticks) 
    print(df_explo)

    df_average = pd.DataFrame()
    df_average["Free"] = pd.concat([df["4AgentsFree"], df["8AgentsFree"], df["12AgentsFree"],df["16AgentsFree"],df["20AgentsFree"]])
    df_average["NoCommunication"] = pd.concat([df["4AgentsNoComm"], df["8AgentsNoComm"], df["12AgentsNoComm"],df["16AgentsNoComm"],df["20AgentsNoComm"]])
    df_average["DistanceFree"] = pd.concat([df["4AgentsDistanceFree"], df["8AgentsDistanceFree"], df["12AgentsDistanceFree"],df["16AgentsFree"],df["20AgentsDistanceFree"]])
    df_average["Distance"] = pd.concat([df["4AgentsDistance"], df["8AgentsDistance"], df["12AgentsDistance"],df["16AgentsDistance"],df["20AgentsDistance"]])

    d_columns = df_explo[["20AgentsFree", "20AgentsNoComm"]]
    d_c_tt = df[["20AgentsFree", "20AgentsNoComm"]]
    print(d_columns)
    print(d_c_tt)
    d_rows = d_columns[(d_c_tt["20AgentsFree"] == 300.0) & (d_c_tt["20AgentsNoComm"] == 300.0)]
    d_rows.plot.bar(rot=45)

    


    # df_to_plot
    # print(df_to_plot)

    print("T_TEST free - random: " , ttest_rel(df_free["FreeRandom"], df_free["Free"]))
    print("T_TEST disturbed - free: " , ttest_rel(df_free["FreeDisturbed"], df_free["Free"]))
    print("T_TEST free - zeroed: " , ttest_rel(df_free["FreeZeroed"], df_free["Free"]))
    # print("T_TEST free - noComm: " , ttest_rel(df_to_plot["average_NoComm"], df_to_plot["average_Free"]))
    # print("T_TEST randominside - free: " , ttest_rel(df_to_plot["average_Inside"], df_to_plot["average_Free"]))
    
    # df_to_plot.mean().plot.bar(rot=45, legend = False)
    sns.boxplot(df_to_plot)
    plt.title("Distributions of time to target ")
    plt.xlabel("Model")
    plt.ylabel("Time to target")
    # df_20 = df[["20NewConfigFree", "20NewConfig"]]
    # df_20.plot.bar(rot=45)


    columns = parse_columns(columns=df.columns, to_include = [ "Free", "NoComm","Distance"], to_not_include= [ "Inside","Zeroed","Random","Disturbed","Inside"])



    swarms_sizes = [4,8,12,16,20]
    fig, axs = plt.subplots(1,len(swarms_sizes))
    fig2, axs2 = plt.subplots(1,len(swarms_sizes))

    my_pal = {"NoComm": "g", "Distance": "b", "DistanceFree":"m","Free":"r"}

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

        df_swarm = df[columns_swarm]


        mp = {
        
        }

        for k in my_pal:
            mp.update({str(swarm) +"Agents"+ k : my_pal[k]})

        print(mp)
        # c = df_swarm.columns.tolist()
        # c.sort(key=lambda x:df_swarm[x].median(), reverse=True)
        # df_swarm = df_swarm[c]

        df_swarm.mean().plot.bar(rot=45, ax = axs2[i], legend = False)
        sns.boxplot(df_swarm,ax= axs[i], palette = mp)


        df_swarm.mean().plot.bar(rot=45, ax = axs2[i], legend = False)

        labels = []
        for l in axs[i].get_xticklabels():
            if swarm < 10:
                labels.append(l.get_text()[7:])
            else:
                labels.append(l.get_text()[8:])

        # axs[i].set_xticklabels(labels,rotation=0,size="medium")
        axs[i].set_title(str(swarm) + " Agents")
        axs2[i].set_xticklabels(labels,rotation=45)
        axs2[i].set_title(str(swarm) + " Agents")

        if i==0:
            
            axs[i].set_ylabel("Time to Target") 
            axs2[i].set_ylabel("Time to Target") 

    from matplotlib.lines import Line2D
    cmap = plt.cm.coolwarm    

    # fig.legend(["NoCommunication", "Distance", "Free", "DistanceFree"])
    # handles, _ = axs.get_legend_handles_labels()          # Get the artists.
    # fig.legend(handles, ["Free", "Distance","DistanceFree", "NoCommunication"], loc="best") 
    

    
    custom_lines = [Line2D([0], [0], color=my_pal[k], lw=4) for k in my_pal]

    fig.legend(custom_lines, ["NoCommunication", "Distance", "DistanceFree","Free"])

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



