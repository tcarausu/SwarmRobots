import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
import seaborn as sns
from numpy.fft import *



def filter_signal(signal, threshold=1e8):
    fourier = rfft(signal)
    frequencies = rfftfreq(signal.size, d=20e-3/signal.size)
    fourier[frequencies > threshold] = 0
    return irfft(fourier)

def sample(signal, kernel_size):
    sampled = np.zeros((signal.shape[0], signal.shape[1], signal.shape[2]//kernel_size))
    for i in range(signal.shape[2]//kernel_size):
        begin = kernel_size * i
        end = min(kernel_size * (i + 1), signal.shape[2])
        sampled[:, :, i] = np.mean(signal[:, :, begin:end], axis=2)
    return sampled

folder = os.path.dirname(__file__) 
os.chdir(folder)

l = []
names = []

for i in range(1,21):
    name = '20Agent2ndrun('+str(i)+')_'
    # with open('../FreeCommunicationLog/BigMaze/Communication_Test'+s+'.txt', 'r') as f:
    with open(f'{folder}//{name}.txt', 'r') as f:
        
        comm = [float(line[:-1].replace(",",".")) for line in f]
        if len(comm) > 7523:
            comm = comm[:7523]
            l.append(comm)
            names.append(name)


a = {}
for list, name in zip(l,names):
    a[name] = list



df = pd.DataFrame(a)
print(df.iloc[:,4:].describe())

sns.violinplot(df)
plt.xticks(range(len(names)), [n[-4:] for n in names])

# # plt.show()
# plt.figure()
# plt.plot(df.loc[:,"Communication_Test(19).txt"])
# plt.plot(df.loc[:,"Communication_Test(1).txt"],c ="g")
plt.figure()
plt.plot(df.mean())
plt.scatter(range(len(df.mean())),df.mean(),c = "r")
plt.xticks(range(len(names)), [n[-4:] for n in names])

# plt.figure()
# plt.plot(sample(df.iloc[:,15]),100)
# plt.plot(sample(df.iloc[:,16]),100)
# plt.show()

# plt.figure()
# plt.plot(rfft(df.iloc[:,15]))
# plt.plot(df.iloc[:,15], c = "g")

# plt.plot(filter_signal(df.iloc[:,16]),1e-3)
# plt.show()

positions = []
pos_names = []
for i in [13,15]:
    name = 'Test ('+str(i)+')X'
    with open(f'{folder}//{name}.txt', 'r') as f:
        
        comm = [float(line[:-1].replace(",",".")) for line in f]
        positions.append(comm)
        pos_names.append(name)


    name = 'Test ('+str(i)+')Z'
    with open(f'{folder}//{name}.txt', 'r') as f:
        
        comm = [float(line[:-1].replace(",",".")) for line in f]
        positions.append(comm)
        pos_names.append(name)

a = {}
for list, name in zip(positions,pos_names):
    a[name] = list

df_positions = pd.DataFrame(a)
print(df_positions)

c_13 = [c for c in df_positions.columns if "13" in c]
df_13 = df_positions[c_13]


c_15 = [c for c in df_positions.columns if "15" in c]
df_15 = df_positions[c_15]

fig, axs = plt.subplots(1,2)
axs[0].scatter(df_13.iloc[:,0], df_13.iloc[:,1], label = "Agent13", s=0.5)
axs[0].scatter(df_15.iloc[:,0], df_15.iloc[:,1],  label = "Agent15",s=0.5)
axs[0].set_xlim(-400,400)
axs[0].set_ylim(-400,400)
axs[0].legend()

print(df.columns)
axs[1].plot(df.loc[:,"20Agent2ndrun(13)_"])
axs[1].plot(df.loc[:,"20Agent2ndrun(15)_"])
plt.show()



