import torch
import torch.nn as nn
import torch.nn.functional as F




class Network(torch.nn.Module):
  def __init__(
    self,
    input_size,
    output_size
  ):
    """
    Creates a neural network that takes as input a batch of images (3
    dimensional tensors) and outputs a batch of outputs (1 dimensional
    tensors)
    """
    super(Network, self).__init__()

    self.layer1 = nn.Linear(input_size, 128)
    self.layer2 = nn.Linear(128, 128)
    self.layer3 = nn.Linear(128,output_size)

  def forward(self, obs):
    obs = F.relu(self.layer1(obs))
    obs = F.relu(self.layer2(obs))
    obs = self.layer3(obs)
    return obs
