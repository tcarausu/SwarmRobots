from mlagents_envs.environment import UnityEnvironment, ActionTuple
from src import *
from src.util import *
import json
import numpy as np
import os
import argparse 
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
from mlagents_envs.side_channel.environment_parameters_channel import EnvironmentParametersChannel
import pickle


def get_env(file_name, no_graphics, training, config):

    parameter_channel = EnvironmentParametersChannel()

    for k in config["penalties"]:
        parameter_channel.set_float_parameter(key=k, value=config["penalties"][k])
    for k in config["rewards"]:
        parameter_channel.set_float_parameter(key=k, value=config["rewards"][k])

    engine_config_channel = EngineConfigurationChannel()

    if training:    
        engine_config_channel.set_configuration_parameters(width=800, height=800, quality_level=1,time_scale=20.,
                                                 target_frame_rate=-1, capture_frame_rate=60)
    else:
        engine_config_channel.set_configuration_parameters(width=800, height=800, quality_level=1,
                                                 target_frame_rate=-1, capture_frame_rate=60)
         
    if file_name is None:
        print("Start game in Unity..")
    else:
        print("Connecting to env..." )
    env = UnityEnvironment(file_name=file_name, no_graphics=no_graphics, seed = 42, worker_id=get_worker_id() if file_name != None else 0,  side_channels=[parameter_channel, engine_config_channel]) 
    
    env.reset()
    behavior_name = list(env.behavior_specs)[0]
    decision_steps, _ = env.get_steps(behavior_name)
    
    if len(decision_steps.obs) > 1: #using comm
        rayc = decision_steps.obs[0]
        comm = decision_steps.obs[1]

        info = f'''
        Using communication.
        
        Number of agents: {comm.shape[0]}

        Observation space size: {comm.shape[1]}
        Raycast size : {rayc.shape[1]}
        '''
        return env, comm.shape[0], comm.shape[1] + rayc.shape[1], info

    else:
        rayc = decision_steps.obs[0]

        info = f'''
        Not using communication.
        Number of agents: {rayc.shape[0]}
        Observation space size: {rayc.shape[1]}
        '''
        
        return env, rayc.shape[0], rayc.shape[1], info
    
def test(num_episodes, brain, env, file, model_name, identifier, step_to_resume):

    env.reset()
    brain.load_weights(file,identifier, model_name, step_to_resume)
    brain.is_training = False
    brain.eval() 


    behavior_name = list(env.behavior_specs)[0]

    episode_reward = {}

    decision_steps, terminal_steps = env.get_steps(behavior_name)
    
    for agent_name in decision_steps:
        episode_reward[agent_name] = 0.
    
    done = False
    for episode in range(num_episodes):

        if done:
            env.reset()
            decision_steps, terminal_steps = env.get_steps(behavior_name)
            done = False
        # env.reset()
        
        step = 0

        while not done:

            step += 1
            print(step)
            
            movement = brain.select_action(get_unique_obs(decision_steps.obs))
            
            # print(movement.continuous if movement.continuous.shape[1] != 0 else movement.discrete)
            env.set_actions(behavior_name, movement)
           
            env.step()
            
            decision_steps, terminal_steps = env.get_steps(behavior_name)

            for agent_name in decision_steps:
                episode_reward[agent_name] += decision_steps[agent_name].reward
            for agent_name in terminal_steps: 
                episode_reward[agent_name] += terminal_steps[agent_name].reward
                print("Agent: %d, episode: %d : reward: %1.3f" %(agent_name, episode,episode_reward[agent_name]))
                episode_reward[agent_name] = 0.
                done = True
            if step>100:
                done = True
                break

def parse_json(file):
    with open(file, "r") as f:
        return json.load(f)

def print_log_info(path,infos):
    print(infos)
    with open(path + "config.txt", "w") as f:
        f.write(infos)


if __name__ =="__main__":

    set_seed()


    parser = argparse.ArgumentParser(description='SwarmRobots')

    parser.add_argument('--env_name', default="MULTIAGENT_DISCRETE_8agent_random", type = str)
    parser.add_argument('--type', default="discrete", type=str)
    parser.add_argument('--identifier', default="Discrete", type=str)
    parser.add_argument("--config_file", default="test1", type=str)
    parser.add_argument('--warmup', default=1000, type=int)
    parser.add_argument('--num_iterations', default=1_000_000, type=int)
    parser.add_argument('--mode', default="train", type=str)
    parser.add_argument('--model_step', default="", type=str)
    parser.add_argument('--on_unity', default="", type = str)
    parser.add_argument("--hidden_neurons", default=256, type=int)
    parser.add_argument("--resume_model", default="", type=str)



    args = parser.parse_args()

    #---FILES

    # folder = os.path.basename(__file__) #folder 
    folder = os.path.dirname(os.path.abspath(__file__))
    print(folder)
    env_name = args.env_name #name of the environment and of the model (we need it also when we are testing a model on unity)
    identifier = "//" + args.identifier + "//"   #run identifier

    #ensure results, data and model folders are properly set

    if not os.path.isdir(folder + "//results//" + args.env_name + "//" + args.identifier): 
        os.makedirs(folder + "//results//" + args.env_name + "//" + args.identifier)
    
    
    if not os.path.isdir(folder + "//data//" + args.env_name + "//" + args.identifier):
        os.makedirs(folder + "//data//" + args.env_name + "//" + args.identifier)


    if not os.path.isdir(folder + "//model//" + env_name + "//" + args.identifier):
        os.makedirs(folder + "//model//" + env_name + "//" + args.identifier)
    

    #file where the environment is. If we want to attach the code to unity, it has to be None
    file_name = folder + "//binary//" + env_name if args.on_unity != "on_unity" else None


    config = parse_json(folder + "//config//" + args.config_file + ".json")
    

    #----HYPERPARAMETERS

    warmup = args.warmup #number of initial steps where actions are chosen randomly. Needed in ddpg to fill memory, still useful in dqn

    num_iterations = args.num_iterations #number of iterations

    #---MODEL

    using_discrete = args.type == "discrete"

    action_size = 7 if using_discrete else 2

    training = args.mode == "train"



    infos = f'''

    Mode: {args.mode}

    Environment name: {env_name}
    Type of action: {args.type}
    Number of action: {action_size}

    Run identifier: {identifier}
    Warmup: {warmup}
    Number of iterations: {num_iterations}

    Number of layers : 2
    Number of hidden neurons: {args.hidden_neurons}

    Configuration file: {args.config_file}

    "penalties" : 
        "existenctial" : {config["penalties"]["existenctial"]},
        "near_agent" : {config["penalties"]["near_agent"]},
        "hit_wall" : {config["penalties"]["hit_wall"]},
        "hit_agent" :{config["penalties"]["hit_agent"]},
    

    "rewards" : 
        "checkpoint" : {config["rewards"]["checkpoint"]}
        "near_target" :{config["rewards"]["near_target"]}
        "target" : {config["rewards"]["target"]}
    
    '''

    resume_model = True if args.resume_model != "" else False

    if training:

        env, number_of_agents, observation_size, info = get_env(file_name, True, training, config)

        infos += info

        print_log_info(folder + "//model//" + env_name + identifier, infos)

        if resume_model:
            with open(f"{folder}//model//{args.env_name}{identifier}model", "rb") as f:
                agent = pickle.load(f)
                agent.epsilon = 0.5

        agent = DQN(nb_states = observation_size, nb_actions = action_size, n_agents = number_of_agents, max_iterations=num_iterations, hidden_neurons = args.hidden_neurons) if using_discrete else\
                DDPG(nb_states = observation_size, nb_actions = action_size, n_agents = number_of_agents, max_iterations=num_iterations, hidden_neurons = args.hidden_neurons)

        trainer = TrainerMultiAgent(agent=agent,folder = folder,env_name = env_name, identifier = identifier)
                    
        try:
            trainer.train(env = env, warmup = warmup)
        finally:
            trainer.log()
            trainer.save_model()
    
    
    else:
        env, number_of_agents, observation_size, info = get_env(file_name, False, training, config)

        agent = DQN(nb_states = observation_size, nb_actions = action_size, n_agents = number_of_agents, max_iterations=num_iterations, hidden_neurons = args.hidden_neurons) if using_discrete else\
                DDPG(nb_states = observation_size, nb_actions = action_size, n_agents = number_of_agents, max_iterations=num_iterations, hidden_neurons = args.hidden_neurons)

        test(num_episodes = 10, brain = agent, env = env, file = folder, model_name = env_name , step_to_resume =  args.model_step, identifier = identifier)
