
from .experience import *
from .ddpg import DDPG
from .util import *
import json


class TrainerMultiAgent:

    def __init__(self, agent, file_to_save, env_name):

        self.agent = agent
        self.log_steps = []
        self.log_policy_losses = []
        self.log_episodes = []

        self.file_to_save = file_to_save
        self.env_name = env_name


    def log(self):
        with open(f"{self.file_to_save}/results/{self.env_name}/log.json", 'w') as f:
            json.dump({"policy" : self.log_policy_losses, "episodes" : self.log_episodes}, f)
        

    def train(self, resume_model, env, identifier, warmup):
        
        if resume_model:
            self.agent.load_weights(self.file_to_save, identifier, self.env_name)
        

        behavior_name = list(env.behavior_specs)[0]

        self.agent.is_training = True

        step = 0 #total iterations
        episode = {} #episode
        episode_steps = {} #steps of the episode
        episode_reward = {}
        reset = {}

        

        log_steps = []
        log_policy_losses = []
        log_episodes = []

        done = False
        
        decision_steps, terminal_steps = env.get_steps(behavior_name)

        self.agent.initialize_states_actions(decision_steps)

        self.agent.reset_random_process()

        for agent_id in decision_steps:
            self.agent.update_obs(agent_id, get_unique_obs(decision_steps[agent_id].obs)) 
            episode[agent_id] = 0
            episode_reward[agent_id] = 0.
            episode_steps[agent_id] = 0
            reset[agent_id] = False
        
        print("Start training...")

        while step < self.agent.max_iterations:

            

            log_steps.append(step)

            if terminal_steps:  
                self.agent.reset_random_process()
                decision_steps, terminal_steps = env.get_steps(behavior_name)
                for agent_id in decision_steps:
                    self.agent.update_obs(agent_id,get_unique_obs(decision_steps[agent_id].obs))

            if step < warmup:
                action_tuple = self.agent.random_action()
            else:
                # action = self.agent.select_action(self.get_unique_obs(normalize_states(decision_steps.obs)))
                action_tuple = self.agent.select_action(get_unique_obs(decision_steps.obs))

            env.set_actions(behavior_name, action_tuple)
            env.step()
            
            decision_steps, terminal_steps = env.get_steps(behavior_name)

            for agent_id in terminal_steps:
                done = True
                reward = terminal_steps[agent_id].reward
                
                observation = get_unique_obs(terminal_steps[agent_id].obs)

                self.agent.observe(agent_id, reward, observation,done)

                print('Agent {}, #{}: episode_reward:{} episode steps:{}'.format(agent_id, episode[agent_id],episode_reward[agent_id],episode_steps[agent_id]))


                self.log_episodes.append([{"agent" : agent_id}, {"episode_reward" : episode_reward[agent_id]}, {"episode_steps" : episode_steps[agent_id]}])

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
                loss = self.agent.update_policy(step)
                self.log_policy_losses.append(loss.item())
                if step % 100 == 0:
                    print(f"Step number {step}, saving_model")
                    self.agent.save_model(self.file_to_save, identifier, self.env_name)

            step += 1

        self.log()   
            
        # print(episode)
        # print(episode_reward)
        # print(episode_steps)


        # with open(f"Results/{env_name}/Episode reward_{env_name}_{identifier}.json", 'w') as f:
        #     json.dump(episode_reward, f)

        
    

    