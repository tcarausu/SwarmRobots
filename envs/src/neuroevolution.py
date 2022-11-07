import numpy as np
import random
from deap import base
from deap import creator
from deap import tools

import time

from mlagents_envs.environment import ActionTuple


class NeuroAgent():

    def __init__(self, env, input_size, action_size, n_layers, n_neurons):
        self.env = env
        self.input_size = input_size
        self.action_size = action_size

        self.n_layers = n_layers
        self.n_neurons = n_neurons

        self.model = NeuroModel(self.input_size, self.action_size, self.n_layers, self.n_neurons)
        self.n_params = self.model.count_params()

        np.random.seed(42)

    def set_deap(self):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        toolbox = base.Toolbox()
        toolbox.register("weight_init", np.random.randn)
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.weight_init, self.n_params)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        toolbox.register("evaluate", self.evaluate)
        toolbox.register("mate", tools.cxUniform, indpb = 0.1)
        toolbox.register("mutate", tools.mutGaussian, mu = 0, sigma = 1, indpb=0.1)
        toolbox.register("select", tools.selTournament, tournsize=2)
        
        return toolbox

    def evaluate(self,individual):
        model = NeuroModel(self.input_size, self.action_size,self.n_layers, self.n_neurons)
        model.set_weights(individual)

        behavior_name = list(self.env.behavior_specs)[0]
        totals = list()
        num_episodes = 5
        totals = []

        for _ in range(num_episodes):
            self.env.reset()
            decision_steps, terminal_steps = self.env.get_steps(behavior_name)
            agent = decision_steps.agent_id[0]
            done = False 
            episode_rewards = 0

            while not done:
                if len(decision_steps) >= 1:
                    action = ActionTuple()
                    movement = model.forward(decision_steps[agent].obs[0])
                    action.add_continuous(movement)
                    self.env.set_actions(behavior_name, action)
                self.env.step()
                decision_steps, terminal_steps = self.env.get_steps(behavior_name)
                if agent in decision_steps: # The agent requested a decision
                    episode_rewards += decision_steps[agent].reward
                if agent in terminal_steps: # The agent terminated its episode
                    episode_rewards += terminal_steps[agent].reward
                    done = True
            totals.append(episode_rewards)
        return (np.sum(totals)/num_episodes,)

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

    def train(self):

        print("---PREPARING POPULATION---")

        toolbox = self.set_deap()
        pop = toolbox.population(n=100) #create population
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

            if mean > 0.6:
                break
            print(time.time()-t)

        self.save_best(pop)        
           
    def save_best(self,pop):
        best_ind = sorted(pop, key=lambda ind: ind.fitness, reverse=True)[0] 
        print(best_ind)
        np.savetxt("best.dat", np.array(best_ind))


class NeuroModel():

    def __init__(self, observation_size, action_size, n_layers, n_neurons):

        self.weights = [np.zeros((observation_size, n_neurons))]

        for _ in range(n_layers):
            self.weights.append(np.zeros((n_neurons, n_neurons)))

        self.weights.append(np.zeros((n_neurons, action_size)))

        self.biases = [np.zeros(self.weights[0].shape[1])]

        for _ in range(n_layers):
            self.biases.append(np.zeros(n_neurons))

        # self.weights = [
        #     np.zeros((observation_size, 100)),
        #     np.zeros((100, 100)),
        #     np.zeros((100, action_size))
        # ]

        # self.biases = [
        #     np.zeros(self.weights[0].shape[1]),
        #     np.zeros(self.weights[1].shape[1]),
        #     np.zeros(self.weights[2].shape[1]),
        # ]

        self.act_fcn = lambda x: np.maximum(0,x)

    def count_params(self):
        sum = 0
        for w in self.weights:
            sum += w.shape[0] * w.shape[1]
        for bias in self.biases:
            sum += bias.shape[0]
        return sum

    def forward(self, x):
        mean = np.mean(x)
        std = np.std(x)

        x = (x-mean) / std
        for i in range(len(self.weights)):
            x = x@self.weights[i]
            if i != (len(self.weights) - 1):
                x -= self.biases[i]
                x = self.act_fcn(x)
        x = x/10
        return x.reshape(1,2)

    def set_weights(self, weights_list):
        k=0
        for w in self.weights:
            for i in range(w.shape[0]):
                for j in range(w.shape[1]):
                    w[i][j] = weights_list[k]
                    k+=1
        for b in self.biases:
            for i in range(b.shape[0]):
                b[i] = weights_list[k]
                k+=1
    