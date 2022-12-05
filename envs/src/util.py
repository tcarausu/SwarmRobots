import numpy as np
import torch
import random

USE_CUDA = torch.cuda.is_available()
FLOAT = torch.cuda.FloatTensor if USE_CUDA else torch.FloatTensor

def prRed(prt): print("\033[91m {}\033[00m" .format(prt))
def prGreen(prt): print("\033[92m {}\033[00m" .format(prt))
def prYellow(prt): print("\033[93m {}\033[00m" .format(prt))
def prLightPurple(prt): print("\033[94m {}\033[00m" .format(prt))
def prPurple(prt): print("\033[95m {}\033[00m" .format(prt))
def prCyan(prt): print("\033[96m {}\033[00m" .format(prt))
def prLightGray(prt): print("\033[97m {}\033[00m" .format(prt))
def prBlack(prt): print("\033[98m {}\033[00m" .format(prt))

def normalize_state(state):
        max = np.max(state)
        min = np.min(state)
        
        if max == min: 
            return state
        
        state = (state-min) / (max - min)
        return state

def normalize_states(state):
        max = np.max(state,axis = 1)
        min = np.min(state, axis = 1)


        for i in range(len(max)):
            if (max[i] == min[i] and max[i]==0):
                max[i] = 1 


        state = (state-min[:,None]) / (max[:,None] - min[:,None])
        return state

def get_unique_obs(obs, max_distance = 50):
    if len(obs) > 1:
        if len(obs[0].shape)>1: #batch of observation
            return np.concatenate([obs[0], normalize_states(obs[1])], axis = 1)
        else: #agent observation
            return np.concatenate([obs[0], normalize_state(obs[1])])
    else: #just one obs, can be raycast or communication
        if len(obs[0].shape) > 1:
            return normalize_states(obs[0])
        else:
            return normalize_state(obs[0])

def to_numpy(var):
    return var.cpu().data.numpy() if USE_CUDA else var.data.numpy()

def to_tensor(ndarray, volatile=False, requires_grad=False, dtype=FLOAT):
    
    if volatile:
        with torch.no_grad():
            t =  torch.Tensor(
                ndarray
            ).type(dtype).cpu()
    else:
        t =  torch.Tensor(
                ndarray
            ).type(dtype).cpu()
        
    t.requires_grad = requires_grad
    return t

def soft_update(target, source, tau):
    for target_param, param in zip(target.parameters(), source.parameters()):
        target_param.data.copy_(
            target_param.data * (1.0 - tau) + param.data * tau
        )

def hard_update(target, source):
    for target_param, param in zip(target.parameters(), source.parameters()):
            target_param.data.copy_(param.data)

def get_worker_id(filename="worker_id.dat"):
    with open(filename, 'a+') as f:
        f.seek(0)
        val = int(f.read() or 0) + 1
        f.seek(0)
        f.truncate()
        f.write(str(val))
        return val

def set_seed():
    np.random.seed(42)
    random.seed(42)



