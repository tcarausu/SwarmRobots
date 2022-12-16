
import numpy as np

import torch
import torch.nn as nn
from torch.optim import Adam

from .model import Actor
from .memory import SequentialMemory
from .util import *
from .DRLAlgo import DRLAlgo
from mlagents_envs.environment import ActionTuple

import os

criterion = nn.SmoothL1Loss()

class DQN(DRLAlgo):
    def __init__(self, nb_states, nb_actions, n_agents, max_iterations, hidden_neurons, enable_double_q=True):

        
        super().__init__(nb_states, nb_actions, n_agents, hidden_neurons, max_iterations)

        self.rmsize = 300_000
        self.window_length = 1

        self.batch_size =64
        self.discount = 0.99
        self.depsilon = 1.0 / max_iterations

        self.target_update_freq = 5
        self.enable_double_q = enable_double_q

        self.prate = 0.0001

        self.network = Actor(self.nb_states, self.nb_actions, **self.net_cfg, is_actor=False)
        self.network_target = Actor(self.nb_states, self.nb_actions, **self.net_cfg, is_actor=False)
        self.optimizer  = Adam(self.network.parameters(), lr=self.prate)

        hard_update(self.network_target, self.network) 
        
        self.epsilon = 1.0

        self.memory = SequentialMemory(limit=self.rmsize, window_length=self.window_length)
   

    def update_policy(self, iteration):
        state_batch, action_batch, reward_batch, next_state_batch, terminal_batch = self.memory.sample_and_split(self.batch_size)
        with torch.no_grad():

            if self.enable_double_q:
                selected_actions = torch.argmax(self.network(to_tensor(next_state_batch)), axis=1).unsqueeze(1)
                best_qvals = self.network_target(to_tensor(next_state_batch)).gather(1,selected_actions)

            else:
                target_qvals = self.network_target(to_tensor(next_state_batch, volatile=True))
                best_qvals, _ = torch.max(target_qvals, 1)
                best_qvals = best_qvals.unsqueeze(1)


        y_target = (to_tensor(reward_batch) + (1.0 - to_tensor(terminal_batch)) * self.discount * best_qvals)
        y_target = y_target.squeeze(1)

        qvals = self.network(to_tensor(state_batch))
        selected_qs = qvals.gather(1,to_tensor(action_batch,dtype=torch.int64)).squeeze(1)

        qval_loss = criterion(selected_qs, y_target)

        self.optimizer.zero_grad()
        qval_loss.backward()
        self.optimizer.step()

        if iteration % self.target_update_freq == 0:
            hard_update(self.network_target, self.network)
        
        return qval_loss.detach()

    def eval(self):
        self.network.eval()
        self.network_target.eval()

    def cuda(self):
        self.actor.cuda()
        self.actor_target.cuda()
        self.critic.cuda()
        self.critic_target.cuda()

    

    def random_action(self):
        action = np.random.randint(low=0, high=self.nb_actions,size=(self.n_agents,1))
        self.update_recent_actions(action)
        action_tuple = ActionTuple()
        action_tuple.add_discrete(action)
        return action_tuple


    def select_action(self, s_t):
        
        self.epsilon -= self.depsilon
        if np.random.uniform() < self.epsilon and self.is_training == 1.:
            return self.random_action()
        else:
            with torch.no_grad():
                output = self.network(to_tensor(s_t, volatile=True))
                action = torch.argmax(output,1).numpy().reshape(self.n_agents,1)

        self.update_recent_actions(action)

        action_tuple = ActionTuple()
        action_tuple.add_discrete(action)

        return action_tuple
        

    def load_weights(self, file_to_save,identifier,env, step):
        file_to_save += "//data//"  + env +"//" + identifier

        self.network.load_state_dict(
            torch.load('{}/network_{}_{}.pkl'.format(file_to_save,env + identifier[2:-2] , step))
        )

        hard_update(self.network_target, self.network)

    def save_model(self,file_to_save,identifier,env, step):
        file_to_save += "//data//" + env + identifier
        torch.save(
            self.network.state_dict(),
            '{}/network_{}_{}.pkl'.format(file_to_save,env + identifier[2:-2], step)
        )

    
    
    