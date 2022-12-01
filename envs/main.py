from mlagents_envs.environment import UnityEnvironment, ActionTuple
from src import *
from src.util import *

import numpy as np
import os



def get_env(file_name, no_graphics):
    env = UnityEnvironment(file_name=file_name, no_graphics=no_graphics, worker_id=get_worker_id()) 
    # env = UnityEnvironment(file_name=None, no_graphics=no_graphics, worker_id=0) 

    env.reset()
    behavior_name = list(env.behavior_specs)[0]
    decision_steps, _ = env.get_steps(behavior_name)
    if len(decision_steps)>1: #using comm
        comm = decision_steps.obs[0]
        rayc = decision_steps.obs[1]
        return env, comm.shape[0], comm.shape[1] + rayc.shape[1]
    else:
        obs = decision_steps.obs[0]
        return env, obs.shape[0], obs.shape[1]
    
def test_ddpg(num_episodes, brain, env, file, env_name, identifier, num_agents):

    env.reset()
    brain.load_weights(file,identifier, env_name)
    brain.is_training = False
    brain.eval() 

    behavior_name = list(env.behavior_specs)[0]
    
    for episode in range(num_episodes):

        decision_steps, terminal_steps = env.get_steps(behavior_name)
        
        # name = decision_steps.agent_id[0]
        episode_reward = {}

        for agent_name in decision_steps:
            episode_reward[agent_name] = 0.

        step = 0

        done = False

        while not done:

            step += 1
            print(step)

            if len(decision_steps) == num_agents:

                action = ActionTuple()
                movement = brain.select_action(get_unique_obs(decision_steps.obs), decay_epsilon = False).reshape(num_agents,action_size)
                print(movement)
                action.add_continuous(movement)
                env.set_actions(behavior_name, action)
            
            env.step()
            
            decision_steps, terminal_steps = env.get_steps(behavior_name)

            for agent_name in decision_steps:
                episode_reward[agent_name] += decision_steps[agent_name].reward
            for agent_name in terminal_steps: 
                episode_reward[agent_name] += terminal_steps[agent_name].reward
                print("Agent: %d, episode: %d : reward: %1.1f" %(agent_name, episode,episode_reward))
                done = True




if __name__ =="__main__":

    set_seed()

    folder = os.path.dirname(__file__)

    env_name = "MULTIAGENT_DISCRETE"
    
    identifier = "//Discrete//"
    
    file_name = folder + "//binary//" + env_name    

    # -------------------------- HYPERPARAMETERS
    
    action_size = 7

    num_iterations = 
    max_episode_length = 2000
    warmup = 1 #number of actions to perform randomly before starting to use the policy
    
    
    # -------------------------- 

    TRAIN = True

    
    if TRAIN:
        env, number_of_agents, observation_size = get_env(file_name, True)

        agent = DQN(nb_states = observation_size, nb_actions = action_size, n_agents = number_of_agents, max_iterations=num_iterations)

        trainer = TrainerMultiAgent(agent=agent,file_to_save = folder,env_name = env_name,)
                    
        try:
            trainer.train(resume_model = False, env = env,identifier=identifier, warmup = warmup)
        except KeyboardInterrupt:
            trainer.log()
                      
    else:
        env, number_of_agents, observation_size = get_env(file_name, False)

        agent = DQN(nb_states = observation_size, nb_actions = action_size, n_agents = number_of_agents, max_iterations=num_iterations)

        test_ddpg(num_episodes = 10, brain = agent, env = env, file = folder, env_name = env_name, identifier = identifier, num_agents=number_of_agents)



    # ----------- JUST SOME RANDOM CODE

    # experiences = []
    # cumulative_rewards = []
    
    # for n in range(1000):
    #     print(n)
    #     new_exp,rewards = trainer.generate_trajectories(env)
    #     np.random.shuffle(experiences)
    #     if len(experiences) > max_length:
    #         experiences = experiences[:max_length]
    #     experiences.extend(new_exp)
        
    #     trainer.update_q_net(experiences, num_actions)
    #     _, rewards = trainer.generate_trajectories(env)
    #     cumulative_rewards.append(rewards)
    #     print("Training step ", n+1, "\treward ", rewards)
    
    # ---------------------------------------


    # ----------------------------------- CODE to try an env

    # file_name = os.path.dirname(__file__) + "//ROLLERBALLsw" #use this to run the binary file
    # file_name = None use this to run the environment started from unity
    
    # env = get_env(file_name)

    # behavior_name = list(env.behavior_specs)[0]
    # spec = env.behavior_specs[behavior_name]
    # for episode in range(3):
    #     env.reset()
    #     decision_steps, terminal_steps = env.get_steps(behavior_name)
        
    #     done = False 
    #     episode_rewards = 0
        
    #     while not done:
            
    #         for agent in decision_steps:
    #             print(len(decision_steps.obs), decision_steps.obs[0].shape,decision_steps.obs[1].shape)
    #             # agent = decision_steps.agent_id[0]
    #             action = ActionTuple()
    #             movement = np.zeros((6,2))
    #             action.add_continuous(movement)
    #             env.set_actions(behavior_name, action)
    #             env.step()
    #         decision_steps, terminal_steps = env.get_steps(behavior_name)
    #         if agent in decision_steps: # The agent requested a decision
    #             episode_rewards += decision_steps[agent].reward
    #         if agent in terminal_steps: # The agent terminated its episode
    #             episode_rewards += terminal_steps[agent].reward
    #             done = True
    #     print(f"Total rewards for episode {episode} is {episode_rewards}")
    # env.close()
    # -----------------------------------

    # -------------- Neuroevolution. it works with rollerball, not sure with swarm robots


    # TRAIN = True #set false to test a saved individual
    # file_save_results = "best.dat"

    # env = get_env(file_name)
    # behavior_name = list(env.behavior_specs)[0]
    # env.reset()
    # decision_steps, terminal_steps = env.get_steps(behavior_name)

    # n_of_agents = len(decision_steps)

    # array_in_input = len(decision_steps.obs) #not sure if okay but rn it works

    # input_size = 12 #just use positions rn


    # num_actions = 2 #don't really know how to get it automatically but they are 2 for the majority of envs so let's keep it like this

    # hidden_layers = 1
    # n_neurons = 100

    
    # neuro_agent = NeuroAgent(env, input_size,num_actions,n_of_agents, hidden_layers, n_neurons)

    # if TRAIN:
    #     neuro_agent.train(file_save_results)
    # else:
    #     test(env, neuro_agent) 

    # -----------------------------------
    # def test_neuro(env, agent, n_layers, n_neurons):

    #     model = NeuroModel(8, 2,  n_layers, n_neurons)
    #     model.set_weights(np.loadtxt("best.dat", dtype=np.float32))

    #     behavior_name = list(env.behavior_specs)[0]
        
    #     for _ in range(3):

    #         decision_steps, terminal_steps = env.get_steps(behavior_name)

    #         agent = decision_steps.agent_id[0]
    #         done = False 

    #         while not done:
    #             if len(decision_steps) >= 1:
    #                 action = ActionTuple()
    #                 movement = model.forward(decision_steps[agent].obs)
    #                 print(movement)
    #                 action.add_continuous(movement)
    #                 env.set_actions(behavior_name, action)
    #             env.step()
    #             decision_steps, terminal_steps = env.get_steps(behavior_name)
    #             if agent in terminal_steps: 
    #                 print(terminal_steps[agent].reward)
    #                 done = True
        












        