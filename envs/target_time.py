import matplotlib.pyplot as plt
import os



os.chdir(os.path.dirname(__file__)) ## go to envs
os.chdir("..//OurModels")


models = os.listdir()

time_values = list()
mazes_names = ["ToyMazeTest", "SmallMazeTest", "MediumMazeTest", "BigMazeTest"]
difficulties = ["Close","Medium","Far"]

for model in models:
    files = os.listdir(model)
    model_list = list()
    for file in mazes_names:
        with open(f"{model}//{file}.dat","r") as f:
            
            for line in f:
                line = line[:-1] if line[-1]=="\n" else line
                model_list.append(float(line[:-1].replace(",",".")))
    time_values.append(model_list)
            

plt.title("Comparison between agents without communication")

for i in range(len(models)):
    plt.plot(time_values[i], label = models[i])

x_ticks = [name + difficulty for name in mazes_names for difficulty in difficulties]
plt.xticks(range(len(x_ticks)), x_ticks , size='xx-small', rotation = 45)
plt.xlabel("Target difficulty ->")
plt.ylabel("Time to reach target [s]")

plt.legend()
plt.show()

