import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import os
import numpy as np
import pandas as pd
import seaborn as sns
from function import *

plt.style.use("ggplot")


if __name__ == "__main__":


    mazes_names = ["ToyMazeTest", "SmallMazeTest", "MediumMazeTest", "BigMazeTest"]

    n_tests = [3,6,18,30] #number of tests (targets) for each maze

    x_ticks = [name + str(n+1)  for name,n_test in zip(mazes_names,n_tests) for n in range(n_test)] #list of strings like maze name + test number for each target

    plot = "TimeToTarget"

    time_values, models = get_time_values(mazes_names,plot)  #time values is a N_MODELS * N_MAZES matrix

    df = pd.DataFrame(np.array(time_values).T, columns=models,index=x_ticks) #store data in a dataframe. We transpose the values so that each model is in a column

    #------- First graph: compare different sizes of swarms not using communication

    columns = parse_columns(columns=df.columns, to_include = ["NoComm"]) #get columns containing NoComm

    df_no_comm = df[columns] #create dataframe with only those columns


    ax = df_no_comm.mean().plot.bar(y="mean",legend = False, rot = 0) #plot mean

    labels = []

    #set custom x_labels
    for i,label in enumerate(ax.get_xticklabels()):
        if i < 2:
            labels.append(f"{label.get_text()[0]} {label.get_text()[1:7]}")
        else:
            labels.append(f"{label.get_text()[0:2]} {label.get_text()[2:8]}")

    ax.set_xticklabels(labels)
    plt.ylabel("Average time to target [s]")

    # Data for table showing unfound targets
    print(df_no_comm[df_no_comm==300.0].count()/len(df_no_comm) * 100)



    #------- Second graph: compare communication types and non communication

    comm_types = [ "NoComm","Free","Distance","Position","DistanceFree","FreePosition"]

    #select columns
    columns = parse_columns(columns=df.columns, to_include = comm_types, to_not_include= ["Zeroed","Inside","Random","Disturbed"])
    
    swarms_sizes = [4,8,12,16,20]

    fig, axs = plt.subplots(1,len(swarms_sizes))

    #colors we'll set to create the custom legend
    colors_list = ["indianred","gold","blueviolet","lightcyan","palegreen", "lightpink"]

    colors_map = dict(zip(comm_types,colors_list))

    for i, swarm in enumerate(swarms_sizes):

        #select only columns related to a swarm size
        columns_swarm = [c for c in columns if c.startswith(str(swarm))]

        columns_swarm.insert(0, columns_swarm.pop(2)) #place no comm at the beginning

        #select data
        df_swarm = df[columns_swarm]


        current_colors_map = {}

        #we need this to give names starting by the swarm size we are currently examining
        for comm_type in colors_map:
            current_colors_map.update({str(swarm) +"Agents"+ comm_type : colors_map[comm_type]})

        sns.boxplot(df_swarm,ax= axs[i], palette = current_colors_map)

        axs[i].set_title(str(swarm) + " Agents")

        #set y label only in the first subplot to make figure clearer
        if i==0:
            axs[i].set_ylabel("Time to Target") 

    #create custom legend
    custom_lines = [Line2D([0], [0], color=colors_map[comm], lw=4) for comm in comm_types]

    fig.legend(custom_lines, list(colors_map.keys()))

    #------- Third graph: compare communication types and unfound targets in big maze by 20 agents swarms

    comm_types = [ "Free","NoComm","Distance","Position","DistanceFree"]

    
    columns = parse_columns(columns=df.columns, to_include = comm_types, to_not_include= ["Zeroed", "Inside","Random","Disturbed","NoNear","NoExist"])
    columns_20 = [c for c in columns if c.startswith("20")]

    df_20_big_maze = df[columns_20].iloc[-30:]

    #count number of values = 300.0
    df_count = df_20_big_maze[df_20_big_maze == 300.0].count()
    
    columns_20.sort(reverse=True, key=lambda x: df_count.loc[x])
    df_count = df_count[columns_20]

    d = df_count.to_dict()
    for k in d:
        d[k] *= 100 / len(df_20_big_maze)
        d[k] = round(d[k],2)

    labels = [c[8:] for c in columns_20]

    plt.figure()
    ax = plt.bar(*zip(*d.items()))
    plt.xticks(ticks = range(len(labels)),labels= labels)
    plt.bar_label(ax)
    plt.ylabel("Percentage of unfound targets")


    #------- Fourth graph: compare free communication with disturbed ones

    df_free = pd.DataFrame()

    df_free["Free"] = pd.concat([df["4AgentsFree"], df["8AgentsFree"], df["12AgentsFree"],df["16AgentsFree"],df["20AgentsFree"]])
    df_free["FreeDisturbed"] = pd.concat([df["4AgentsFreeDisturbed"], df["8AgentsFreeDisturbed"], df["12AgentsFreeDisturbed"],df["16AgentsFreeDisturbed"],df["20AgentsFreeDisturbed"]])
    df_free["FreeRandom"] = pd.concat([df["4AgentsFreeRandom"], df["8AgentsFreeRandom"], df["12AgentsFreeRandom"],df["16AgentsFreeRandom"],df["20AgentsFreeRandom"]])    
    df_free["FreeZeroed"] = pd.concat([df["4AgentsFreeZeroed"], df["8AgentsFreeZeroed"], df["12AgentsFreeZeroed"],df["16AgentsFreeZeroed"],df["20AgentsFreeZeroed"]])    

    plt.figure()
    sns.boxplot(df_free)
    plt.ylabel("Time to target")


    #------- Fifth graph: compare exploration rate in unfound target

    explo_values, models = get_time_values(mazes_names, "ExplorationRate")
    df_explo = pd.DataFrame(np.array(explo_values).T, columns=models,index=x_ticks) 

    comm_types = [ "Free","NoComm","Distance","Position","DistanceFree"]

    columns = parse_columns(columns=df_explo, to_include = comm_types, to_not_include= ["Zeroed", "Inside","Random","Disturbed","NoNear","NoExis"])

    columns_16 = [c for c in columns if c.startswith("8")]

    df_explo_16 = df_explo[columns_16][-30:]
    df_time_16 = df[columns_16][-30:]



    df_explo_not_to_target = df_explo_16[df_time_16[columns_16] == 300.0].dropna()
    df_explo_not_to_target *= 100 #to display percentage
    
    print(df_explo_not_to_target)
    
    fig,axs = plt.subplots(1,len(df_explo_not_to_target) - 2)

    for i in range(len(axs)):
        df_explo_not_to_target.iloc[i,:].plot.bar(ax = axs[i])

        labels = []
        for l in axs[i].get_xticklabels():
            labels.append(l.get_text()[7 :])

        axs[i].set_xticklabels(labels,rotation=0)
        axs[i].set_title(df_explo_not_to_target.index[i])

        if i==0:
            axs[i].set_ylabel("")


    #------- Sixth graph - compare different rewards in boxplot



    
    # df_rewards = pd.DataFrame()

    # df_rewards["Free"] = pd.concat([df["4AgentsFree"], df["8AgentsFree"], df["12AgentsFree"],df["16AgentsFree"],df["20AgentsFree"]])
    # df_rewards["NoNearAgent"] = pd.concat([df["4NoNearAgentFree"], df["8NoNearAgentFree"], df["12NoNearAgentFree"],df["16NoNearAgentFree"],df["20NoNearAgentFree"]])
    # df_rewards["NoExistential"] = pd.concat([df["4NoExistentialFree"], df["8NoExistentialFree"], df["12NoExistentialFree"],df["16NoExistentialFree"],df["20NoExistentialFree"]])    

    # plt.figure()
    # sns.boxplot(df_rewards)
    # plt.ylabel("Time to target")

    # #------- Seventh graph - compare different rewards in unfound targets

    # columns = parse_columns(columns=df_explo, to_include = ["Free","NoNear","NoExis"], to_not_include= ["Zeroed", "Inside","Random","Disturbed","Distance"])
    
    # columns_20 = [c for c in columns if c.startswith("20")]
    
    # df_20_big_maze = df[columns_20].iloc[-30:]

    # #count number of values = 300.0
    # df_count = df_20_big_maze[df_20_big_maze == 300.0].count()
    
    # columns_20.sort(reverse=True, key=lambda x: df_count.loc[x])
    # df_count = df_count[columns_20]

    # d = df_count.to_dict()
    # for k in d:
    #     d[k] *= 100 / len(df_20_big_maze)
    #     d[k] = round(d[k],2)

    # # labels = [c[8:] for c in df_20_big_maze]

    # plt.figure()
    # ax = plt.bar(*zip(*d.items()))
    # # plt.xticks(ticks = range(len(labels)),labels= labels)
    # plt.bar_label(ax)
    # plt.ylabel("Percentage of unfound targets")


    # #------- Eighth graph - compare different rewards in explo rate


    # explo_values, models = get_time_values(mazes_names, "ExplorationRate")
    # df_explo = pd.DataFrame(np.array(explo_values).T, columns=models,index=x_ticks) 

    # comm_types = [ "Free","NoNear","NoExis"]

    # columns = parse_columns(columns=df_explo, to_include = comm_types, to_not_include= ["Zeroed", "Inside","Random","Disturbed","NoComm","Distance","Position","DistanceFree"])

    # columns_16 = [c for c in columns if c.startswith("20")]

    # df_explo_16 = df_explo[columns_16][-30:]
    # df_time_16 = df[columns_16][-30:]

    # df_explo_not_to_target = df_explo_16[df_time_16[columns_16] == 300.0].dropna()
    # df_explo_not_to_target *= 100 #to display percentage

    
    # fig,axs = plt.subplots(1,len(df_explo_not_to_target))

    # for i in range(len(axs)):
    #     df_explo_not_to_target.iloc[i,:].plot.bar(ax = axs[i])

    #     labels = []
    #     for l in axs[i].get_xticklabels():
    #         labels.append(l.get_text())

    #     axs[i].set_xticklabels(labels,rotation=0)
    #     axs[i].set_title(df_explo_not_to_target.index[i])

    #     if i==0:
    #         axs[i].set_ylabel("")
    







    #-----------------------------------------------------------------------------------------

    plt.show()


