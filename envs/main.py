from mlagents_envs.environment import UnityEnvironment, ActionTuple
from src import *
import numpy as np
import os


def get_env():
    file_name = os.path.dirname(__file__) + "//ROLLERBALL"
    env = UnityEnvironment(file_name=file_name, no_graphics=True) #set false to visualize
    env.reset()
    return env

if __name__ =="__main__":
    
    env = get_env()
    behavior_name = list(env.behavior_specs)[0]
    spec = env.behavior_specs[behavior_name]
    for episode in range(3):
        env.reset()
        decision_steps, terminal_steps = env.get_steps(behavior_name)
        agent = decision_steps.agent_id[0]
        done = False 
        episode_rewards = 0
        while not done:
            if len(decision_steps) >= 1:
                action = ActionTuple()
                movement = np.array([1,0]).reshape(1,2)
                action.add_continuous(movement)
                env.set_actions(behavior_name, action)
            env.step()
            decision_steps, terminal_steps = env.get_steps(behavior_name)
            if agent in decision_steps: # The agent requested a decision
                episode_rewards += decision_steps[agent].reward
            if agent in terminal_steps: # The agent terminated its episode
                episode_rewards += terminal_steps[agent].reward
                done = True
        print(f"Total rewards for episode {episode} is {episode_rewards}")



    env.close()









    # trajectories = []
    # buffer = []
    # input_size = 8
    # num_actions = 2

    # network = Network(input_size = 8, output_size = num_actions)

    # max_length = 20000

    # trainer = Trainer(network=network, buffer_size=10)
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