
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

class DDPG(DRLAlgo):
    def __init__(self, nb_states, nb_actions,max_iterations, n_agents, hidden_neurons):
        
        super().__init__(nb_states, nb_actions, n_agents,hidden_neurons, max_iterations)

        self.prate = 0.0001
        self.rate = 0.001
        self.rmsize = 300_000
        self.window_length = 1
        self.ou_theta = 0.15
        self.ou_mu = 0.0
        self.ou_sigma = 0.2

        self.batch_size =64
        self.tau = 0.001
        self.discount = 0.99
        self.depsilon = 1.0 / max_iterations
        
        self.actor = Actor(self.nb_states, self.nb_actions, **self.net_cfg)
        self.actor_target = Actor(self.nb_states, self.nb_actions, **self.net_cfg)
        self.actor_optim  = Adam(self.actor.parameters(), lr=self.prate)

        self.critic = Critic(self.nb_states, self.nb_actions, **self.net_cfg)
        self.critic_target = Critic(self.nb_states, self.nb_actions, **self.net_cfg)
        self.critic_optim  = Adam(self.critic.parameters(), lr=self.rate)

        hard_update(self.actor_target, self.actor) 
        hard_update(self.critic_target, self.critic)
        
        #Create replay buffer
        self.memory = SequentialMemory(limit=self.rmsize, window_length=self.window_length)
        self.random_process = OrnsteinUhlenbeckProcess(size=nb_actions, theta=self.ou_theta, mu=self.ou_mu, sigma=self.ou_sigma)


    

    def update_policy(self):
        # Sample batch
        state_batch, action_batch, reward_batch, \
        next_state_batch, terminal_batch = self.memory.sample_and_split(self.batch_size)

        with torch.no_grad():
            next_q_values = self.critic_target([
                to_tensor(next_state_batch, volatile=True),
                self.actor_target(to_tensor(next_state_batch, volatile=True)),
            ])

        target_q_batch = to_tensor(reward_batch) + \
            self.discount*to_tensor(terminal_batch.astype(np.float))*next_q_values #output of target critic - yi

        # Critic update
        self.critic.zero_grad()

        q_batch = self.critic([ to_tensor(state_batch), to_tensor(action_batch) ]) #output of critic - Q(si,ai)
        
        value_loss = criterion(q_batch, target_q_batch)
        value_loss.backward()

        self.critic_optim.step()

        # Actor update
        self.actor.zero_grad()

        policy_loss = -self.critic([
            to_tensor(state_batch),
            self.actor(to_tensor(state_batch))
        ]) #update of the actor

        policy_loss = policy_loss.mean() 
        policy_loss.backward()

        self.actor_optim.step()

        # Target update
        soft_update(self.actor_target, self.actor, self.tau)
        soft_update(self.critic_target, self.critic, self.tau)


        return policy_loss.detach()

    def eval(self):
        self.actor.eval()
        self.actor_target.eval()
        self.critic.eval()
        self.critic_target.eval()

    def cuda(self):
        self.actor.cuda()
        self.actor_target.cuda()
        self.critic.cuda()
        self.critic_target.cuda()

    def random_action(self):
        action = np.random.uniform(-1.,1.,(self.n_agents,self.nb_actions))    
        self.update_recent_actions(action)
        action_tuple = ActionTuple()
        action_tuple.add_continuous(action.reshape((self.n_agents,self.nb_actions)))
        return action_tuple

    def select_action(self, s_t):

        action = to_numpy(
            self.actor(to_tensor([s_t]))
        ).squeeze(0)

        action += self.is_training*max(self.epsilon, 0)*self.random_process.sample()
        
        
        self.epsilon -= self.depsilon

        action = np.clip(action, -1., 1.)
        
        self.update_recent_actions(action)

        action_tuple = ActionTuple()
        action_tuple.add_continuous(action.reshape((self.n_agents,self.nb_actions)))

        return action_tuple
        
    def reset_random_process(self):
        self.random_process.reset_states()


    def load_weights(self, file_to_save,identifier,env, step):
        file_to_save += "//data" + identifier 

        self.actor.load_state_dict(
            torch.load('{}/actor_{}.pkl'.format(file_to_save,  + identifier[2:-2] + "_" + step))
        )

        self.critic.load_state_dict(
            torch.load('{}/critic_{}.pkl'.format(file_to_save, env + identifier[2:-2] + "_" + step))
        )

    def save_model(self,file_to_save,identifier,env, step):
        file_to_save += "//data" + identifier
        torch.save(
            self.actor.state_dict(),
            '{}/actor_{}_{}.pkl'.format(file_to_save,env, step)
        )
        torch.save(
            self.critic.state_dict(),
            '{}/critic_{}_{}.pkl'.format(file_to_save,env,step)
        )

    
    
    