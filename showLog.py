from matplotlib import animation
import numpy as np
import matplotlib.pyplot as plt

import time

# First set up the figure, the axis, and the plot element we want to animate
fig = plt.figure()
ax = fig.add_subplot(111)

ax.set_xlim([0, 2000])
ax.set_ylim([-1, 1])


line, = ax.plot([],[],'b-', animated=True)
# getFrame() makes a call to the CCD frame buffer and retrieves the most recent frame

# animation function
count = 0
def update(frame):
    global count
    with open('Communication_Test.txt', 'r') as f:
        comm = [float(line[:-1].replace(",",".")) for line in f][:count]
        count+=1
    line.set_xdata(list(range(len(comm))))
    line.set_ydata(comm)
    ax.set_xlim([max(len(comm)-2000, 0), max(2000, len(comm)+10)])
    return line,


# call the animator
anim = animation.FuncAnimation(fig, update, interval=1000, blit=True)
plt.show()