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

# end = ""
end = "Free"#-->get models without communication
# end = "Free" #-->get model with free communication


##---


os.chdir(os.path.dirname(__file__)) ## go to envs
os.chdir("..//OurModels//TimeToTarget")

models = os.listdir()


for model in models: #get all models in the folder
    if model.endswith(end): #remove if not in our scope
        models.remove(model)

print(models)
time_values = list()
# mazes_names = ["ToyMazeTest", "SmallMazeTest", "MediumMazeTest", "BigMazeTest"]
mazes_names = ["ToyMazeTest", "SmallMazeTest",  "BigMazeTest"]
difficulties = ["Close","Medium","Far"]

x_ticks = [name + difficulty for name in mazes_names for difficulty in difficulties] #create a list with maze+target names



for model in models: #for each model
    model_list = list()
    for file in mazes_names: #for each maze
        with open(f"{model}//{file}.dat","r") as f:
            for line in f:
                line = line[:-1] if line[-1]=="\n" else line #delete '\n' at the end of first n-1 rows
                model_list.append(float(line[:-1].replace(",","."))) #save number as float (c# saves float with comma)
    time_values.append(model_list)

#sort models by swarm size. since each name is associated to a list, we have to do this
time_values, models = zip(*sorted(zip(time_values, models), key=lambda x: sort_by_initial(x[1]))) 


plt.title("Comparison between agents without communication")

for i in range(len(models)):
    plt.plot(time_values[i], label = models[i]) 


plt.xticks(range(len(x_ticks)), x_ticks , size='xx-small', rotation = 45)
plt.xlabel("Target difficulty ->")
plt.ylabel("Time to reach target [s]")
plt.legend()
# plt.show()


#---------------------------------------
#transpose time_values so that models are on the columns and targets on rows
df = pd.DataFrame(np.array(time_values).T, columns=models,index=x_ticks)

print(df)
df_normalized = df.apply(norm, axis = 1) #normalize rows

mean_df = pd.DataFrame({
    "models" : models,
    "mean" : df_normalized.mean(axis=0)
})


mean_df.plot.bar(x="models",y="mean",rot=45,title = "Mean time to reach target",legend = False)

plt.xticks(size='xx-small')
plt.xlabel("Model")
plt.ylabel("Normalized mean")

#---------------------------------------

# fig,ax = plt.subplots(1,1)
plt.figure()
sns.boxplot(data=df)


# 4 and 8 are skewed towards right which is a bad thing

#---------------------------------------


fig, axes = plt.subplots(1,len(mazes_names))
fig.tight_layout(pad=5.0)

axs = axes.flatten()

#here we want to plot times needed to complete each target. so we have to transpose again the dataframe so that columns are targets.
df_t = df.transpose() 
print(df_t)

for i, (maze, ax) in enumerate(zip(mazes_names, axs)):
    sns.boxplot(data = df_t.iloc[:,i*3:i*3+3], ax=ax)
    ax.set_title(f"{maze}")
    ax.set_xticks(range(len(difficulties)),difficulties)
    ax.set_xticklabels(ax.get_xticklabels(),rotation=45,size="xx-small")


# ax = sns.boxplot(x=df.index)  

plt.show()

#---------------------------------------

# data = [[ 66386, 174296,  75131, 577908,  32015],
#         [ 58230, 381139,  78045,  99308, 160454],
#         [ 89135,  80552, 152558, 497981, 603535],
#         [ 78415,  81858, 150656, 193263,  69638],
#         [139361, 331509, 343164, 781380,  52269]]

# columns = ('Freeze', 'Wind', 'Flood', 'Quake', 'Hail')
# rows = ['%d year' % x for x in (100, 50, 20, 10, 5)]

# data = np.array(time_values).T

# columns = models
# rows = x_ticks

# values = np.arange(0, 200, 200)
# value_increment = 200

# # # Get some pastel shades for the colors
# colors = plt.cm.BuPu(np.linspace(0, 1, len(rows)))
# n_rows = len(data)

# index = np.arange(len(columns)) + 0.3
# bar_width = 0.4

# # # Initialize the vertical-offset for the stacked bar chart.
# y_offset = np.zeros(len(columns))

# # # Plot bars and create text labels for the table
# cell_text = []

# for row in range(n_rows):
#     # plt.bar(index, data[row], bar_width, bottom=y_offset, color=colors[row])
#     # y_offset = y_offset + data[row]
#     cell_text.append(['%1.1f' % (x / 1000.0) for x in y_offset])
# # Reverse colors and text labels to display the last value at the top.
# colors = colors[::-1]
# cell_text.reverse()

# # # Add a table at the bottom of the axes
# the_table = plt.table(cellText=cell_text,
#                       rowLabels=rows,
#                       rowColours=colors,
#                       colLabels=columns,)

# # Adjust layout to make room for the table:
# # plt.subplots_adjust(left=0.2, bottom=0.2)
# plt.ylabel("Time to reach target")
# plt.yticks(values * value_increment, ['%d' % val for val in values])
# plt.xticks([])
# plt.title('Loss by Disaster')
# plt.show()

