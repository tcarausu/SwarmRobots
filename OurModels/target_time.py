import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
import seaborn as sns
from function import *



if __name__ == "__main__":

    mazes_names = ["ToyMazeTest", "SmallMazeTest", "MediumMazeTest", "BigMazeTest"]
    # mazes_names = ["ToyMazeTest", "SmallMazeTest", "MediumMazeTest"]

    # difficulties = ["Close","Medium","Far"]
    n_tests = [3,6,18,30]

    #create a list with maze+target names that will represent the x-axis
    x_ticks = [name + str(n+1)  for name,n_test in zip(mazes_names,n_tests) for n in range(n_test) ] 

    plot = "TimeToTarget"
    time_values, models = get_time_values(mazes_names,plot)


    #plot a line connecting times for each swarm. This graph is a bit messy
    for i in range(len(models)):
        plt.plot(time_values[i], label = models[i]) 

    
    

    plt.xticks(range(len(x_ticks)), x_ticks , size='xx-small', rotation = 45)
    plt.xlabel("Target difficulty ->")
    plt.ylabel("Time to reach target [s]")
    plt.legend()
    plt.title("Comparison between agents without communication")
    # plt.show()


    #---------------------------------------

    #transpose time_values so that models are on the columns and targets on rows. 
    df = pd.DataFrame(np.array(time_values).T, columns=models,index=x_ticks)

    print(df)


    print(df[(df>200) & (df<300)].count())

    # We have a max number of steps fixed to 15000, which results in 5 minutes of exploration time.
    # To make data "agnostic" with respect to this value, we can normalize rows (performance of models in each
    # target). We can normalize in 2 ways: with respect to the maximum exploration time (300 seconds), thus 
    # mantaining proportions between performances but ending up having different scales in bar plots, or 
    # normalize between 0 and 1, which would make all rows consistent but distorting values (give more importance
    # to models that got to the target). The parameter with respect to max time
    # decides the normalization


    df_normalized = df.apply(norm, respect_to_max_time=True, axis = 1) #normalize rows

    # select only the columns we are interested in. The following selects only models without communication
    columns = [c for c in df_normalized.columns]
    df_to_plot = df_normalized[columns]

    #create dataframe to easily plot means. One row for each model, one columns containing normalized mean
    mean_df = pd.DataFrame({
        "mean" : df_to_plot.mean(axis=0)
    })

    print(mean_df)

    mean_df.plot.bar(y="mean",rot=45, title = "Mean time to reach target",legend = False)

    plt.xticks(size='xx-small')
    plt.xlabel("Model")
    plt.ylabel("Normalized mean")

    #---------------------------------------


    plt.figure()

    #select columns to plot in boxplots

    # this is going to plot data about columns, so data about each model and distribution of his times
    # columns is the list with the models that will be plotted

    sns.boxplot(data=df_normalized[columns])
    plt.xticks(size='xx-small')
    plt.title("Comparison between agents without communication.")
    plt.xlabel("Model")
    plt.ylabel("Normalized mean")


    plt.figure()
    sns.boxplot(data=df[columns])
    plt.xticks(size='xx-small')
    plt.title("Comparison between agents without communication.")
    plt.xlabel("Model")
    plt.ylabel("Mean")

    


    #---------------------------------------
    # fig, axes = plt.subplots(1,len(mazes_names))
    # fig.tight_layout(pad=5.0)

    # axs = axes.flatten()

    # #here we want to plot times needed to complete each target. we have to transpose again the dataframe so that columns are targets.
    # df_t = df.transpose() 
    # n = len(n_tests)


    # Distribution of "target to time" in each target for each maze. It shows that
    # easy target are actually easier than medium and so on.
    # This is computed over all models
    # for i, (maze, ax) in enumerate(zip(mazes_names, axs)):
    #     sns.boxplot(data = df_t.iloc[:,i*n:i*n+n], ax=ax) 
    #     ax.set_title(f"{maze}")
    #     ax.set_xticks(range(n),n_tests)
    #     ax.set_xticklabels(ax.get_xticklabels(),rotation=45,size="xx-small")
    #     ax.set_xlabel("Target complexity")
    #     ax.set_ylabel("Time to target")



    plt.show()
