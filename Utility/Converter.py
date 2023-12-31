import copy
import torch
import numpy as np

class Converter():
    def __init__(self, distance_type, zero_distance,device):
        self.pow_2_level = 0
        self.distance_type = distance_type
        self.zero_distance = zero_distance
        self.device = device

    def increase_pow_2_level(self):
        self.pow_2_level += 1

    def reset(self):
        self.pow_2_level = 0

    def convert_to_pows_of_2(self, weights, first = False):
         import math
         c = copy.deepcopy(weights.detach()).type_as(weights)
         if first:
             c[torch.abs(c) < self.zero_distance] = 0 # set small values to be zero
         c[c > 0] = torch.pow(2, torch.max(torch.Tensor([-7 - self.pow_2_level]).type_as(weights), torch.round(torch.log2(c[c>0]))))
         a = torch.log2(torch.abs(c[c < 0]).type_as(weights))
         c[c < 0] = -torch.pow(2, torch.max(torch.Tensor([-7 - self.pow_2_level]).type_as(weights), torch.round(a)))
         return c


    def convert_to_add_pows_of_2(self, weights, distance):
        current = self.convert_to_pows_of_2(weights, True)
        for x in range(self.pow_2_level):
            diff = weights - current
            next = torch.zeros(len(weights)).type_as(weights)
            diff_pow_2 = self.convert_to_pows_of_2(diff)
            if self.distance_type == "relative":
                diff_dist = torch.abs(distance *  weights)
            else:
                diff_dist = distance
            to_change = torch.abs(diff) > diff_dist
            to_change = torch.logical_and(to_change, current !=0)
            next[to_change] = diff_pow_2[to_change]
            current = next + current
        return current

    def round_to_precision(self, weights, distance):
        return self.convert_to_add_pows_of_2(weights, distance)
