import numpy as np
import random
from deap import base
from deap import creator
from deap import tools

import time

from mlagents_envs.environment import ActionTuple


class NeuroAgent():

    def __init__(self, env, input_size, action_size,n_of_agents, hidden_layers, n_neurons):
        self.env = env
        self.input_size = input_size
        self.action_size = action_size
        self.n_of_agents = n_of_agents

        self.hidden_layers = hidden_layers
        self.n_neurons = n_neurons

        self.hidden_layers = hidden_layers
        self.n_neurons = n_neurons

        self.model = NeuroModel(self.input_size, self.action_size, self.hidden_layers, self.n_neurons)
        self.n_params = self.model.count_params()

        np.random.seed(42)

    def weight_init(self):
        ind = []

        for i in range(len(self.model.weights)):
            
            current_w = self.model.weights[i] 
            np_weight = np.random.randn(current_w.shape[0],current_w.shape[1] ) *  np.sqrt(2 / (current_w.shape[0] + current_w.shape[1]))
            ind.append(list(map(list,np_weight))) 

            if i != len(self.model.weights) - 1: #add bias only if it's not the last layer
                ind.append(np.zeros(current_w.shape[1]))
            
        return ind


    def set_deap(self):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        toolbox = base.Toolbox()
        toolbox.register("weight_init", self.weight_init)
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.weight_init, 1)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        toolbox.register("evaluate", self.evaluate)
        toolbox.register("mate", tools.cxUniform, indpb = 0.1)
        toolbox.register("mutate", tools.mutGaussian, mu = 0, sigma = 1, indpb=0.1)
        toolbox.register("select", tools.selTournament, tournsize=2)
        
        return toolbox

    def evaluate(self,individual):
        model = NeuroModel(self.input_size, self.action_size,self.hidden_layers, self.n_neurons)
        model.set_weights(individual)

        behavior_name = list(self.env.behavior_specs)[0]
        totals = list()
        num_episodes = 1
        max_steps = 750
        totals = []

        for _ in range(num_episodes):
            self.env.reset()
            decision_steps, terminal_steps = self.env.get_steps(behavior_name)
            
            done = False 
            episode_reward = 0
            steps = 0
            while not done and steps<max_steps:
                steps += 1
                for agent_id_terminated in terminal_steps:
                    episode_reward += terminal_steps[agent_id_terminated].reward
                for agent_id_decision in decision_steps:
                    episode_reward += decision_steps[agent_id_decision].reward

                if len(decision_steps) >= 1:
                    action = ActionTuple()
                    movement = model.forward(decision_steps.obs[1])
                    action.add_continuous(movement)
                    self.env.set_actions(behavior_name, action)
                    self.env.step()
                    decision_steps, terminal_steps = self.env.get_steps(behavior_name)
                
                else:
                    done = True
            totals.append(episode_reward)
        return (np.mean(totals),)

    def mateAndMutate(self,offspring, toolbox):
        CXPB, MUTPB = 0.2, 0.5
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

    def findFitness(self,pop):
        fits = [ind.fitness.values for ind in pop]
        return fits, np.mean(fits)

    def train(self,file):

        print("---PREPARING POPULATION---")

        toolbox = self.set_deap()
        pop = toolbox.population(n=75) #create population
        fitnesses = list(map(toolbox.evaluate, pop)) #evaluation of each individual
        
        for ind, fit in zip(pop, fitnesses): #assign eval to each individual
            ind.fitness.values = fit 

        epochs = 1000

        print("---START TRAINING---")
        
        for g in (range(epochs)):
            print(g)
            t = time.time()
            offspring = toolbox.select(pop, len(pop))
            offspring = list(map(toolbox.clone, offspring))
            self.mateAndMutate(offspring, toolbox)

            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(toolbox.evaluate, invalid_ind)
            
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            pop[:] = offspring

            fits, mean = self.findFitness(pop)

            if g%30 == 0:
                print("Min %s" % min(fits))
                print("Max %s" % max(fits))
                print("Mean %s" % mean)
                self.save_best(pop,file[0:5] + "epoch"+str(g)+".dat")  

            if mean > 0.6:
                break
            print(time.time()-t)

        self.save_best(pop,file)        
           
    def save_best(self,pop,file):
        best_ind = sorted(pop, key=lambda ind: ind.fitness, reverse=True)[0] 
        print(best_ind)
        np.savetxt(file, np.array(best_ind))


class NeuroModel():

    def __init__(self, observation_size, action_size, n_layers, n_neurons):

        self.obs_size = observation_size
        self.act_size = action_size
        
        self.weights = []
        self.biases = []

        self.initialize_weights(n_layers, n_neurons)
        self.initialize_biases(n_layers, n_neurons)

        self.act_fcn = np.tanh

    def initialize_weights(self, n_layers, n_neurons):
        self.weights.append(np.zeros((self.obs_size, n_neurons)))

        for _ in range(n_layers):
            self.weights.append(np.zeros((n_neurons, n_neurons)))

        self.weights.append(np.zeros((n_neurons, self.act_size)))

    def initialize_biases(self, n_layers, n_neurons):
        self.biases.append(np.zeros(self.weights[0].shape[1]))

        for _ in range(n_layers):
            self.biases.append(np.zeros(n_neurons))

    def count_params(self):
        sum = 0
        for w in self.weights:
            sum += w.shape[0] * w.shape[1]
        for bias in self.biases:
            sum += bias.shape[0]
        return sum

    def forward(self, x):
        batch = x.shape[0]

        mean = np.mean(x, axis = 1).reshape(x.shape[0],1)
        std = np.std(x, axis = 1).reshape(x.shape[0],1)

        x = (x-mean) / std
        for i in range(len(self.weights)):
            x = x@self.weights[i]
            if i != (len(self.weights) - 1):
                x -= self.biases[i]
                x = self.act_fcn(x)
        return x.reshape(batch,self.act_size)

    def set_weights(self, ind):
        ind = ind[0]
        weights = ind[0::2]
        biases = ind[1::2]

        self.weights = [np.array(w) for w in weights]
        self.biases = [np.array(b) for b in biases]

    