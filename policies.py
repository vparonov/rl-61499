import random
import torch
import numpy as np 

from onnxutils import loadModelFromOnnx, getPrediction
from model import DQN64
from utils import loadModel


SKIP = 0 
FIFO = 1

class HeuristicPolicy():
    def __init__(self, burstSize=10, waitBetweenBoxes=10, waitBetweenBursts=100):
        self.waitBetweenBursts = waitBetweenBursts
        self.waitBetweenBoxes = waitBetweenBoxes
        self.burstSize = burstSize
        self.burstCounter = 0
        self.waittime = 0
        self.waitbboxes = 0
        self.fifoCount = 0
        self.skipCount = 0

    def __call__(self, ctime, state, remaining_items):
        if remaining_items == 0:
            return SKIP 
        
        if self.waittime == 0:
            if self.burstCounter < self.burstSize:
                if self.waitbboxes == self.waitBetweenBoxes:
                    self.burstCounter += 1  
                    #print(ctime, FIFO, self.burstCounter)
                    self.fifoCount += 1
                    self.waitbboxes = 0
                    return FIFO
                else:
                    self.waitbboxes += 1
            else:
                self.waittime = self.waitBetweenBursts
                self.burstCounter = 0
                #print(ctime, SKIP, self.waittime)
        else:
            self.waittime -= 1
            #print(ctime, SKIP, self.waittime)
        self.skipCount += 1
        return SKIP


class RandomPolicy():
    def __init__(self, minwait, maxwait):
        self.waittime = 0
        self.waittimes = []
        self.minwait = minwait
        self.maxwait = maxwait

    def __call__(self, ctime, state, remaining_items):
        if remaining_items == 0:
            return SKIP 

        if self.waittime == 0:
            self.waittime = random.randint(self.minwait, self.maxwait)
            self.waittimes.append(self.waittime)
            return FIFO
        else:
            self.waittime -= 1
        return SKIP


class StateFullHeuristicPolicy():
    def __init__(self, coefC1=10, coefC2=10, fillMargin=0.75):
        self.fillMargin = fillMargin
        self.coefC1 = coefC1
        self.coefC2 = coefC2

    def __call__(self, ctime, state, remaining_items):
        if remaining_items == 0:
            return SKIP 
        fill = (self.coefC1 * state[1] + self.coefC2 *
                state[2]) / (self.coefC1 + self.coefC2)

        if fill <= self.fillMargin:
            return FIFO
        return SKIP


class RLPolicy():
    def __init__(self, fileName):
         self.model = loadModelFromOnnx(fileName)

    def __call__(self, ctime, state, remaining_items):
        if remaining_items == 0:
            return SKIP
        return getPrediction(self.model, state)

class RLPolicyWithGrad():
    def __init__(self, fileName):
        n_observations = 19
        n_actions = 2
        device = 'cpu'

        model = DQN64(n_observations, n_actions).to(device)

        self.model = loadModel(model, fileName)

    def __call__(self, ctime, state, remaining_items):
        tstate = torch.tensor(state.astype(np.float32)).unsqueeze(0)
        tstate = tstate.to('cpu')
        tstate.requires_grad_()

        output = self.model(tstate)
        action = output.argmax()

        output_max = output[0, action]
        output_max.backward()

        self.saliency = tstate.grad.data.abs().squeeze().cpu().detach().numpy()

        return action.item()