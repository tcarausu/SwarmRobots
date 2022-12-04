
import numpy as np

import torch
import torch.nn as nn
from torch.optim import Adam

from .model import Actor
from .memory import SequentialMemory
from .util import *
from mlagents_envs.environment import ActionTuple

import os

criterion = nn.SmoothL1Loss()

class DQN(object):
    def __init__(self, nb_states, nb_actions, n_agents, max_iterations):

        self.enable_double_q = False
        
        self.nb_states = nb_states
        self.nb_actions= nb_actions
        self.n_agents = n_agents
        self.max_iterations = max_iterations

        self.hidden1 = 512
        self.hidden2 = 512
        self.init_w = 0.003

        self.rmsize = 300_000
        self.window_length = 1

        self.batch_size =64
        self.tau = 0.001
        self.discount = 0.99
        self.depsilon = 1.0 / max_iterations

        self.is_training = True

        self.recent_state = {}
        self.recent_action = {}

        self.target_update_freq = 5


        self.prate = 0.0001
        # self.rate = 0.001
        
        # self.ou_theta = 0.15
        # self.ou_mu = 0.0
        # self.ou_sigma = 0.2

        net_cfg = {
            'hidden1':self.hidden1, 
            'hidden2':self.hidden2, 
            'init_w':self.init_w
        }
        self.network = Actor(self.nb_states, self.nb_actions, **net_cfg, is_actor=False)
        self.network_target = Actor(self.nb_states, self.nb_actions, **net_cfg, is_actor=False)
        self.optimizer  = Adam(self.network.parameters(), lr=self.prate)

        hard_update(self.network_target, self.network) # Make sure target is with the same weight
        
        #Create replay buffer
        self.memory = SequentialMemory(limit=self.rmsize, window_length=self.window_length)

        self.epsilon = 1.0

        # if USE_CUDA: self.cuda()

    def initialize_states_actions(self, decision_steps):
        for agent_id in decision_steps:
            self.recent_state[agent_id] = None
            self.recent_action[agent_id] = None
        

    def update_policy(self, iteration):
        state_batch, action_batch, reward_batch, next_state_batch, terminal_batch = self.memory.sample_and_split(self.batch_size)
        with torch.no_grad():
            # if self._double_q:
            #     # Use online qf to get optimal actions
            #     selected_actions = torch.argmax(self.network(next_state_batch), axis=1)
            #     # use target qf to get Q values for those actions
            #     selected_actions = selected_actions.long().unsqueeze(1)
            #     best_qvals = torch.gather(self.network_target(next_state_batch),
            #                               dim=1,
            #                               index=selected_actions)

            # else:
                target_qvals = self.network_target(to_tensor(next_state_batch, volatile=True))
                best_qvals, _ = torch.max(target_qvals, 1)
                best_qvals = best_qvals.unsqueeze(1)

        # _clip_reward = None
        # if _clip_reward is not None:
        #     rewards_clipped = torch.clamp(reward_batch, -1 * self._clip_reward,
        #                                   self._clip_reward)


        y_target = (to_tensor(reward_batch) +
                    (1.0 - to_tensor(terminal_batch)) * self.discount * best_qvals)
        y_target = y_target.squeeze(1)

        # optimize qf
        qvals = self.network(to_tensor(state_batch))
        # selected_qs = torch.sum(qvals * to_tensor(action_batch), axis=1)
        selected_qs = qvals.gather(0,to_tensor(action_batch,dtype=torch.int64)).squeeze(1)

        if selected_qs.size() != y_target.size():
            print("Oooo")

        qval_loss = criterion(selected_qs, y_target)

        self.optimizer.zero_grad()
        qval_loss.backward()
        self.optimizer.step()

        # # optionally clip the gradients
        # if self._clip_grad is not None:
        #     torch.nn.utils.clip_grad_norm_(self.policy.parameters(),
        #                                    self._clip_grad)

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

    def observe(self, agent_id, r_t, s_t1, done):
        if self.is_training:
            self.memory.append(self.recent_state[agent_id], self.recent_action[agent_id], r_t, done)
            self.update_obs(agent_id,s_t1)

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
                action = torch.argmax(self.network(to_tensor(s_t, volatile=True)),1).numpy().reshape(self.n_agents,1)

        self.update_recent_actions(action)

        action_tuple = ActionTuple()
        action_tuple.add_discrete(action)

        return action_tuple
        
    
    def update_recent_actions(self, action):
        i = 0
        for agent_id in self.recent_action:
            self.recent_action[agent_id] = action[i,:]
            i += 1

    def update_obs(self, agent, obs):
        self.recent_state[agent] = obs
        

    def load_weights(self, file_to_save,identifier,env_name):
        file_to_save += "//data"

        self.network.load_state_dict(
            torch.load('{}/network_{}.pkl'.format(file_to_save + identifier,env_name))
        )

        hard_update(self.network_target, self.network)

    def save_model(self,file_to_save,identifier,env, step):
        file_to_save += "//data" + identifier
        torch.save(
            self.network.state_dict(),
            '{}/network_{}_{}.pkl'.format(file_to_save,env, step)
        )

    def reset_random_process(self):
        pass
    
    