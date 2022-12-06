import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

fig,ax = plt.subplots(1,1)
scatter_positions = ax.scatter([], [])
count = 0
def update(frame):
    count += 1
    print(count)
    
    with open('Communication_Test.txt', 'r') as f:
        comm = [float(line[:-1].replace(",",".")) for line in f]
    scatter_positions.set_offsets([list(range(len(comm))),comm])
    return scatter_positions

anim = FuncAnimation(fig, update, frames=500, interval = 40, repeat = False)
update(0)
plt.show()
anim = 0