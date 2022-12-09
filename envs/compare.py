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
#_--------------------------------------------------------------------


##--- data to plot

# end = "NoComm"
end = "Free"#-->get models without communication
# end = "Free" #-->get model with free communication


##---


os.chdir(os.path.dirname(__file__)) ## go to envs
os.chdir("..//OurModels//TimeToTarget")

models = os.listdir()


time_values = list()
# mazes_names = ["ToyMazeTest", "SmallMazeTest", "MediumMazeTest", "BigMazeTest"]
mazes_names = ["ToyMazeTest", "SmallMazeTest",  "BigMazeTest"]
difficulties = ["Close","Medium","Far"]

x_ticks = [name + difficulty for name in mazes_names for difficulty in difficulties] #create a list with maze+target names

print(models)


for model in models: #for each model
    model_list = list()
    for file in mazes_names: #for each maze
        with open(f"{model}//{file}.dat","r") as f:
            for line in f:
                line = line[:-1] if line[-1]=="\n" else line #delete '\n' at the end of first n-1 rows
                model_list.append(float(line.replace(",","."))) #save number as float (c# saves float with comma)
    time_values.append(model_list)

#sort models by swarm size. since each name is associated to a list, we have to do this
time_values, models = zip(*sorted(zip(time_values, models), key=lambda x: sort_by_initial(x[1]))) 

#time values is a N_MODELS * N_MAZES matrix


df = pd.DataFrame(np.array(time_values).T, columns=models,index=x_ticks)


# for swarm in range(4,21,4):

swarm = "20"

columns = [c for c in df.columns if c.startswith(swarm)]

plt.figure(swarm)
df_swarm = df[columns]
df_swarm.plot.bar(rot=45)

plt.xticks(size='xx-small')
plt.xlabel("Mazes")
plt.ylabel("Time to reach target")
plt.show()

