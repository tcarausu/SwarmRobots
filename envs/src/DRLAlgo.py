
class DRLAlgo():
    def __init__(self, nb_states, nb_actions, n_agents, hidden_neurons, max_iterations):
        self.nb_states = nb_states
        self.nb_actions= nb_actions
        self.n_agents = n_agents

        self.is_training = True
        self.max_iterations = max_iterations

        self.recent_state = {}
        self.recent_action = {}

        self.init_w = 0.003

        self.net_cfg = {
            'hidden1':hidden_neurons, 
            'hidden2':hidden_neurons, 
            'init_w':self.init_w
        }

    def initialize_states_actions(self, decision_steps):
        for agent_id in decision_steps:
            self.recent_state[agent_id] = None
            self.recent_action[agent_id] = None


    def observe(self, agent_id, r_t, s_t1, done):
        if self.is_training:
            self.memory.append(self.recent_state[agent_id], self.recent_action[agent_id], r_t, done)
            self.update_obs(agent_id,s_t1)

    
    def update_recent_actions(self, action):
        i = 0
        for agent_id in self.recent_action:
            self.recent_action[agent_id] = action[i,:]
            i += 1

    def update_obs(self, agent, obs):
        self.recent_state[agent] = obs

    
    def select_action(self, s_t):
        raise NotImplementedError

    def random_action(self):
        raise NotImplementedError

    def load_weights(self,file_to_save,identifier,env_name, step_to_resume):
        raise NotImplementedError


    def reset_random_process(self):
        pass

    def eval(self):
        pass

    def cuda(self):
        pass