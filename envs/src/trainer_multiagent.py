from mlagents_envs.environment import ActionTuple

from .experience import *
from .ddpg import DDPG
from .util import *


class TrainerMultiAgent:

    def __init__(self, observation_size, action_size, number_of_agents,num_iterations = 1):

        self.agent = DDPG(observation_size, action_size, num_iterations)

        self.observation_size = observation_size
        self.action_size = action_size
        self.number_of_agents = number_of_agents
        self.max_distance = 50
        self.num_iterations = num_iterations
        

    def train(self, resume_model, env, file_to_save, identifier,env_name, warmup, num_agents):
        
        if resume_model:
            self.agent.load_weights(file_to_save, identifier, env_name)
        
        # env.reset() env is reset when created

        behavior_name = list(env.behavior_specs)[0]

        self.agent.is_training = True

        step = 0 #total iterations
        episode = {} #episode
        episode_steps = {} #steps of the episode
        episode_reward = {}
        reset = {}


        done = False
        
        decision_steps, terminal_steps = env.get_steps(behavior_name)

        self.agent.initialize_states_actions(decision_steps)

        # name = decision_steps.agent_id[0] #this makes it work for just 1 agent !

        # observation = decision_steps.obs[0]

        self.agent.reset_random_process()

        for agent_id in decision_steps:
            self.agent.update_obs(agent_id, get_unique_obs(decision_steps[agent_id].obs)) 
            episode[agent_id] = 0
            episode_reward[agent_id] = 0.
            episode_steps[agent_id] = 0
            reset[agent_id] = False
        
        while step < self.num_iterations:

            print(step)

            # for agent_id in decision_steps:
            #     if reset[agent_id]:
            #         self.agent.reset_random_process()
            #         self.agent.update_obs(agent_id,decision_steps[agent_id].obs[0])

            if terminal_steps:  
                self.agent.reset_random_process()
                decision_steps, terminal_steps = env.get_steps(behavior_name)
                for agent_id in decision_steps:
                    self.agent.update_obs(agent_id,get_unique_obs(decision_steps[agent_id].obs))

            if step <= warmup:
                action = self.agent.random_action(num_agents)
            else:
                # action = self.agent.select_action(self.get_unique_obs(normalize_states(decision_steps.obs)))
                action = self.agent.select_action(get_unique_obs(decision_steps.obs))
            
            # action_copy = action.copy()
            # action_reshaped = action_copy.reshape(num_agents,self.action_size)

            action_tuple = ActionTuple()
            action_tuple.add_continuous(action.reshape(num_agents,self.action_size))

            env.set_actions(behavior_name, action_tuple)
            env.step()
            
            decision_steps, terminal_steps = env.get_steps(behavior_name)

            for agent_id in terminal_steps:
                done = True
                reward = terminal_steps[agent_id].reward
                
                observation = get_unique_obs(terminal_steps[agent_id].obs)

                self.agent.observe(agent_id, reward, observation,done)

                print('Agent {}, #{}: episode_reward:{} episode steps:{}'.format(agent_id, episode[agent_id],episode_reward[agent_id],episode_steps[agent_id]))

                episode_steps[agent_id] = 0
                episode_reward[agent_id] = 0
                episode[agent_id] += 1

                env.reset()
            
            for agent_id in decision_steps:
                done = False
                reward = decision_steps[agent_id].reward
                observation = get_unique_obs(decision_steps[agent_id].obs)
                self.agent.observe(agent_id,reward,observation,done)

                episode_steps[agent_id] += 1
                episode_reward[agent_id] += reward

            
            # if episode_steps >= max_episode_length:
            #     done = True

            if step > warmup :
                self.agent.update_policy()
                if step % 100 == 0:
                    self.agent.save_model(file_to_save, identifier, env_name)

                

            step += 1

            
            
        print(episode)
        print(episode_reward)
        print(episode_steps)

    
    

    # def generate_trajectories(self, env):
    #     """
    #     Given a Unity Environment and a Q-Network, this method will generate a
    #     buffer of Experiences obtained by running the Environment with the Policy
    #     derived from the Q-Network.
    #     :param BaseEnv: The UnityEnvironment used.
    #     :param q_net: The Q-Network used to collect the data.
    #     :param buffer_size: The minimum size of the buffer this method will return.
    #     :param epsilon: Will add a random normal variable with standard deviation.
    #     epsilon to the value heads of the Q-Network to encourage exploration.
    #     :returns: a Tuple containing the created buffer and the average cumulative
    #     the Agents obtained.
    #     """
        
    #     buffer = []

    #     # Read and store the Behavior Name of the Environment
    #     behavior_name = list(env.behavior_specs)[0]
    #     # Read and store the Behavior Specs of the Environment
    #     spec = env.behavior_specs[behavior_name]

    #     # Create a Mapping from AgentId to Trajectories. This will help us create
    #     # trajectories for each Agents
    #     dict_trajectories_from_agent = {}
    #     # Create a Mapping from AgentId to the last observation of the Agent
    #     dict_last_obs_from_agent = {}
    #     # Create a Mapping from AgentId to the last observation of the Agent
    #     dict_last_action_from_agent = {}
    #     # Create a Mapping from AgentId to cumulative reward (Only for reporting)
    #     dict_cumulative_reward_from_agent = {}
    #     # Create a list to store the cumulative rewards obtained so far
    #     cumulative_rewards = []

    #     while len(buffer) < self.buffer_size:  # While not enough data in the buffer
    #         # Get the Decision Steps and Terminal Steps of the Agents
    #         decision_steps, terminal_steps =env.get_steps(behavior_name)

    #         # permute the tensor to go from NHWC to NCHW
    #         # order = (0, 3, 1, 2)
    #         # decision_steps.obs = [np.transpose(obs, order) for obs in decision_steps.obs]
    #         # terminal_steps.obs = [np.transpose(obs, order) for obs in terminal_steps.obs]

    #         # For all Agents with a Terminal Step:
    #         for agent_id_terminated in terminal_steps:
    #             # Create its last experience (is last because the Agent terminated)
                
    #             last_experience = Experience(
    #                                         obs=dict_last_obs_from_agent[agent_id_terminated].copy(),
    #                                         reward=terminal_steps[agent_id_terminated].reward,
    #                                         done=not terminal_steps[agent_id_terminated].interrupted,
    #                                         action=dict_last_action_from_agent[agent_id_terminated].copy(),
    #                                         next_obs=terminal_steps[agent_id_terminated].obs[0]
    #                                         )
    #             # Clear its last observation and action (Since the trajectory is over)
    #             dict_last_obs_from_agent.pop(agent_id_terminated)
    #             dict_last_action_from_agent.pop(agent_id_terminated)

    #             # Report the cumulative reward
    #             cumulative_reward = (dict_cumulative_reward_from_agent.pop(agent_id_terminated)+ terminal_steps[agent_id_terminated].reward
    #             )
    #             cumulative_rewards.append(cumulative_reward)
    #             # Add the Trajectory and the last experience to the buffer
    #             buffer.extend(dict_trajectories_from_agent.pop(agent_id_terminated))
    #             buffer.append(last_experience)
                

    #         # For all Agents with a Decision Step:
    #         for agent_id_decisions in decision_steps:
    #             # If the Agent does not have a Trajectory, create an empty one
    #             if agent_id_decisions not in dict_trajectories_from_agent:
    #                 dict_trajectories_from_agent[agent_id_decisions] = []
    #                 dict_cumulative_reward_from_agent[agent_id_decisions] = 0

    #             # If the Agent requesting a decision has a "last observation"
    #             if agent_id_decisions in dict_last_obs_from_agent:
    #             # Create an Experience from the last observation and the Decision Step
    #                 exp = Experience(
    #                     obs=dict_last_obs_from_agent[agent_id_decisions].copy(),
    #                     reward=decision_steps[agent_id_decisions].reward,
    #                     done=False,
    #                     action=dict_last_action_from_agent[agent_id_decisions].copy(),
    #                     next_obs=decision_steps[agent_id_decisions].obs[0],
    #                 )
    #                 # Update the Trajectory of the Agent and its cumulative reward
    #                 dict_trajectories_from_agent[agent_id_decisions].append(exp)
    #                 dict_cumulative_reward_from_agent[agent_id_decisions] += (
    #                     decision_steps[agent_id_decisions].reward
    #                 )
    #             # Store the observation as the new "last observation"
    #             dict_last_obs_from_agent[agent_id_decisions] = (
    #             decision_steps[agent_id_decisions].obs[0]
    #             )

    #         # Generate an action for all the Agents that requested a decision
    #         # Compute the values for each action given the observation
    #         actions = (
    #             self.network(torch.from_numpy(decision_steps.obs[0])).detach().numpy()
    #         )

    #         # Add some noise with epsilon to the values
    #         # actions_values += epsilon * (
    #         #     np.random.randn(actions_values.shape[0], actions_values.shape[1])
    #         # ).astype(np.float32)

    #         # Pick the best action using argmax
    #         # actions = np.argmax(actions_values, axis=1)
    #         # print(actions, actions.shape)
    #         # actions.resize((len(decision_steps), 1))
            
    #         # Store the action that was picked, it will be put in the trajectory later
    #         for agent_index, agent_id in enumerate(decision_steps.agent_id):
    #             dict_last_action_from_agent[agent_id] = actions

    #         # Set the actions in the environment
    #         # Unity Environments expect ActionTuple instances.
    #         action_tuple = ActionTuple()
    #         action_tuple.add_continuous(actions)
    #         env.set_actions(behavior_name, action_tuple)
    #         # Perform a step in the simulation
    #         env.step()
    #     return buffer, np.mean(cumulative_rewards)

    # def update_q_net(self, buffer, action_size):
    #     """
    #     Performs an update of the Q-Network using the provided optimizer and buffer
    #     """
    #     BATCH_SIZE = 1000
    #     NUM_EPOCH = 3
    #     GAMMA = 0.9
    #     batch_size = min(len(buffer), BATCH_SIZE)
    #     np.random.shuffle(buffer)

    #     optimizer = torch.optim.Adam(self.network.parameters(), lr= 0.001)
    #     # Split the buffer into batches
    #     batches = [buffer[batch_size * start : batch_size * (start + 1)]for start in range(int(len(buffer) / batch_size))]

    #     for _ in range(NUM_EPOCH):
    #         for batch in batches:
    #             # Create the Tensors that will be fed in the network
    #             obs = torch.from_numpy(np.stack([ex.obs for ex in batch]))
    #             reward = torch.from_numpy(np.array([ex.reward for ex in batch], dtype=np.float32).reshape(-1, 1))
    #             done = torch.from_numpy(np.array([ex.done for ex in batch], dtype=np.float32).reshape(-1, 1))
    #             action = torch.from_numpy(np.stack([ex.action for ex in batch]))
    #             next_obs = torch.from_numpy(np.stack([ex.next_obs for ex in batch]))

    #             # Use the Bellman equation to update the Q-Network
    #             target = (reward + (1.0 - done) * GAMMA * self.network(next_obs).detach())

    #             print(target.shape)
    #             print(action.shape)
    #             # mask = torch.zeros((len(batch), action_size))
    #             # mask.scatter_(1, action, 1)
    #             prediction = torch.sum(self.network(obs), dim=1, keepdim=True)
    #             criterion = torch.nn.MSELoss()
    #             loss = criterion(prediction, target)

    #             # Perform the backpropagation
    #             optimizer.zero_grad()
    #             loss.backward()
    #             optimizer.step()