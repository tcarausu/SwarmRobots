import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
import seaborn as sns



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



def get_time_values(mazes_names, plot):
    
    folder = os.path.dirname(__file__) 
    os.chdir(f"{folder}//ReportData//{plot}")
    models = os.listdir() #get all models in the folder

    time_values = list()

    for model in models: #for each model
        model_list = list()
        for file in mazes_names: #for each maze
            with open(f"{model}//{file}.dat","r") as f: #open file containing data
                for line in f:
                    line = line[:-1] if line[-1]=="\n" else line #delete '\n' at the end of first n-1 rows
                    if len(line) < 2:
                        line += ".0"

                    if "Higher" in model and "Time" in plot:
                        model_list.append(20. * float(line[:-1].replace(",","."))) #save number as float (c# saves float with comma)
                    else:
                        model_list.append(float(line[:-1].replace(",",".")))
                    
        time_values.append(model_list)
        print(len(model_list), model)

    #time values is a N_MODELS * N_MAZES matrix

    #sort models by swarm size. since each name is associated to a list, we have to sort both lists
    time_values, models = zip(*sorted(zip(time_values, models), key=lambda x: sort_by_initial(x[1])))
    return time_values, models 