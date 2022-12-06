import numpy as np

import torch
import torch.nn as nn
from torch.optim import Adam

from .model import (Actor, Critic)
from .memory import SequentialMemory
from .random_process import OrnsteinUhlenbeckProcess
from .util import *
from .DRLAlgo import DRLAlgo

from mlagents_envs.environment import ActionTuple



criterion = nn.MSELoss()

class PPO(DRLAlgo):
    def __init__(self, nb_states, nb_actions,max_iterations, n_agents, hidden_neurons):
        
        super().__init__(nb_states, nb_actions, n_agents,hidden_neurons, max_iterations)

        


    def random_action(self):
        pass

    def select_action(self, s_t):

        pass
        
    

    def load_weights(self, file_to_save,identifier,env_name, step_to_resume):
        file_to_save += "//data" + identifier +"//" + identifier 

        # self.actor.load_state_dict(
        #     torch.load('{}/actor_{}.pkl'.format(file_to_save,  + identifier[2:-2] + "_" + step_to_resume))
        # )

        # self.critic.load_state_dict(
        #     torch.load('{}/critic_{}.pkl'.format(file_to_save, env_name + identifier[2:-2] + "_" + step_to_resume))
        # )

    def save_model(self,file_to_save,identifier,env, step):
        file_to_save += "//data" + identifier
        # torch.save(
        #     self.actor.state_dict(),
        #     '{}/actor_{}_{}.pkl'.format(file_to_save,env, step)
        # )
        # torch.save(
        #     self.critic.state_dict(),
        #     '{}/critic_{}_{}.pkl'.format(file_to_save,env,step)
        # )

    
    
    