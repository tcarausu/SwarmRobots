from mlagents_envs.environment import UnityEnvironment, ActionTuple
from src import *
import numpy as np
import os
import random

def get_worker_id(filename="worker_id.dat"):
    with open(filename, 'a+') as f:
        f.seek(0)
        val = int(f.read() or 0) + 1
        f.seek(0)
        f.truncate()
        f.write(str(val))
        return val

def get_env(file_name, no_graphics):
    env = UnityEnvironment(file_name=file_name, no_graphics=no_graphics, worker_id=get_worker_id()) 
    # env = UnityEnvironment(file_name=None, no_graphics=no_graphics, worker_id=0) 

    env.reset()
    behavior_name = list(env.behavior_specs)[0]
    decision_steps, _ = env.get_steps(behavior_name)
    obs = decision_steps.obs[0]

    return env, obs.shape[0], obs.shape[1]

def test_ddpg(num_episodes, agent, env, file, env_name, num_agents):

    env.reset()
    agent.load_weights(file,env_name)
    agent.is_training = False
    agent.eval() 

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
                movement = agent.select_action(decision_steps.obs, decay_epsilon = False).reshape(num_agents,action_size)
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

            # if step > 100:
            #     env.reset()
            #     break

def set_seed():
    np.random.seed(42)
    random.seed(42)


#----not used right now
def test_neuro(env, agent, n_layers, n_neurons):

    model = NeuroModel(8, 2,  n_layers, n_neurons)
    model.set_weights(np.loadtxt("best.dat", dtype=np.float32))

    behavior_name = list(env.behavior_specs)[0]
    
    for _ in range(3):

        decision_steps, terminal_steps = env.get_steps(behavior_name)

        agent = decision_steps.agent_id[0]
        done = False 

        while not done:
            if len(decision_steps) >= 1:
                action = ActionTuple()
                movement = model.forward(decision_steps[agent].obs)
                print(movement)
                action.add_continuous(movement)
                env.set_actions(behavior_name, action)
            env.step()
            decision_steps, terminal_steps = env.get_steps(behavior_name)
            if agent in terminal_steps: 
                print(terminal_steps[agent].reward)
                done = True

if __name__ =="__main__":

    set_seed()

    folder = os.path.dirname(__file__)
    env_name = "MULTIAGENT"
    
    
    file_name = folder + "/" + env_name  #use this to run the binary file


    # -------------------------- HYPERPARAMETERS
    
    # depends on the binary file
    # observation_size = 8
    action_size = 2
    # number_of_agents = 6


    num_iterations = 200_000
    max_episode_length = 2000
    warmup = 10000 #number of actions to perform randomly before starting to use the policy
    
    
    # -------------------------- 

    TRAIN = True

    
    
    if TRAIN:
        env, number_of_agents, observation_size = get_env(file_name, True)

        trainer = TrainerMultiAgent(observation_size = observation_size, 
                    action_size = action_size, 
                    number_of_agents = number_of_agents
                    )
                    
        trainer.train(resume_model = False,
                      num_iterations = num_iterations, 
                      env = env,
                      file_to_save = folder,
                      env_name = env_name,
                      warmup = warmup,
                      num_agents=number_of_agents)
    else:
        env, number_of_agents, observation_size = get_env(file_name, False)
        test_ddpg(num_episodes = 10, agent = TrainerMultiAgent(observation_size = observation_size, 
                                                                action_size = action_size, 
                                                                number_of_agents = number_of_agents
                                                                ).agent, env = env, file = folder, env_name = env_name, num_agents=number_of_agents)



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

    












    