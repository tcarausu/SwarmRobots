## Deep Learning for Games and Simulations - Python code

This folder contains the implementation of Double Deep Q-Network (DQN) and Deep Deterministic Policy gradient (DDPG) methods to train Unity agents. DQN algorithm is inspired by the one provided by [garage](https://github.com/rlworkgroup/garage) toolkit, while DDPG, memory and some helper functions implementations are based on [this repository](https://github.com/ghliu/pytorch-ddpg).

We eventually decided to use PPO algorithm provided by ML-agents package because of lack of time.


### Requirements
Packages needed to run the project can be installed through the following instruction.

> pip install -r requirements.txt


### Settings

| Name             | Default      | Description                                                                  |
|------------------|--------------|------------------------------------------------------------------------------|
| --env_name       |              | Unity Environment folder name. If on_unity flag is passed, the execution happens there, not in the built file. env_name is still needed when testing to load the model. |
| --action_type    | Discrete     | Discrete or Continuous. If discrete, DQN is used, otherwise DDPG.            |
| --identifier     | FirstRun     | Identifier of the run.                                                       |
| --config_file    | reportReward | File json containing rewards values.                                         |
| --num_iterations | 1000000      | Number of training iterations.                                               |
| --model_step     |              | It indicates the model to select when testing. 
                                    It's needed because DQN can easily diverge, hence the best model is not the last one necessarily.                       |
| --on_unity       |              | Pass "yes" if the code has to run on unity.                             |
| --resume_model   |              | Pass "yes" to resume model for training.                                                             |

Notice that all built environments have to be placed inside [binary](binary) folder.

### Examples

Train environment called "4AgentsNoCommTrain". 

> python main.py --env_name 4AgentsNoCommTrain --identifier FooRun --config_file reportReward --num_iterations 2000000

Train a continuous action environment on unity

> python main.py --on_unity yes --identifier FooRun --config_file reportReward --num_iterations 2000000 --action_type Continuous

Test a model on a built environment. We need to provide the name of the environment, the identifier of the run in which the model was trained and the step that we want to resume the model from. 

> python main.py  --env_name 4AgentsNoCommTrain --identifier TestRun --model_step 12932 --mode test --config_file reportReward


### Visualize training metrics

[analyze.ipynb](analyze.ipynb) contains a function that plots training loss, average episode rewards and average episode steps.
