import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
import seaborn as sns



def sort_by_initial(x):

    for i,c in enumerate(x):
        if not c.isdigit():
            break
    return int(x[:i])

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

    #sort model by swarm size so that they appear ordered in graphs.
    models.sort(key = sort_by_initial)

    for model in models: #for each model
        model_list = list()
        for file in mazes_names: #for each maze
            with open(f"{model}//{file}.dat","r") as f: #open file containing data
                for line in f:
                    line = line[:-1] if line[-1]=="\n" else line #delete '\n' at the end of first n-1 rows
                    if len(line) < 2: #if the value has no decimal, add it
                        line += ".0"
                    
                    number = float(line[:-1].replace(",",".")) #unity uses commas for floating numbers

                    if number < 0 or number > 300.0: 
                        number = 300.0

                    model_list.append(number)
                    
        time_values.append(model_list)

    return time_values, models 




def parse_columns(columns, to_include = [], to_not_include = []):
    new_columns = []
    for c in columns:
        flag = False
        for word in to_include:
            if word in c:
                flag = True
                break
        for word in to_not_include:
            if word in c:
                flag = False
                break
        if flag:
            new_columns.append(c)

    return new_columns       

