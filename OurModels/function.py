import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
import seaborn as sns

folder = os.path.dirname(__file__) 
os.chdir(f"{folder}//ReportData//TimeToTarget")
mazes_names = ["ToyMazeTest", "SmallMazeTest", "MediumMazeTest", "BigMazeTest"]
difficulties = ["Close","Medium","Far"]

#create a list with maze+target names that will represent the x-axis
x_ticks = [name + difficulty for name in mazes_names for difficulty in difficulties] 

def sort_by_initial(x):
    try:
        number = int(x[:2])
    except:
        number = int(x[:1])
    return number

def norm(row, respect_to_max_time = True, max_time = 300):
    if respect_to_max_time:
        return row / max_time
    else:
        max = np.max(row)
        min = np.min(row)
        if(max==min): #nobody got to the target
            return pd.array([1 for _ in row])
        return (row-min)/(max-min)



def get_time_values():
    models = os.listdir() #get all models in the folder

    time_values = list()
    


    for model in models: #for each model
        model_list = list()
        for file in mazes_names: #for each maze
            with open(f"{model}//{file}.dat","r") as f: #open file containing data
                for line in f:
                    line = line[:-1] if line[-1]=="\n" else line #delete '\n' at the end of first n-1 rows
                    model_list.append(float(line[:-1].replace(",","."))) #save number as float (c# saves float with comma)
        time_values.append(model_list)

    #time values is a N_MODELS * N_MAZES matrix

    #sort models by swarm size. since each name is associated to a list, we have to sort both lists
    time_values, models = zip(*sorted(zip(time_values, models), key=lambda x: sort_by_initial(x[1])))
    return time_values, models 