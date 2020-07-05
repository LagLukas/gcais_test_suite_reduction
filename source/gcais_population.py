import sys
import random
from math import floor
try:
    from source.set_cover import *
except Exception as _:
    from set_cover import *


class GCAISPopulation:

    def __init__(self, initial_sol, to_be_covered, border, epsilon, use_epsilon):
        self.table = {}
        self.to_be_covered = to_be_covered
        initial = initial_sol.covered
        self.table[initial] = {}
        self.table[initial]["sols"] = [initial_sol]
        self.table[initial]["cost"] = initial_sol.cost
        self.key_gen = self.get_key_generator()
        self.border = border
        self.epsilon = epsilon
        self.use_epsilon = use_epsilon

    def get_population_size(self):
        total = 0
        for key in self.table.keys():
            total += len(self.table[key]["sols"])
        return total

    def get_key_generator(self):
        for key in self.table.keys():
            yield int(key)

    def try_insert(self, sol):
        cost = sol.cost
        try:
            if self.table[sol.covered]["cost"] > cost:
                self.table[sol.covered]["sols"] = [sol]
                self.table[sol.covered]["cost"] = sol.cost
            elif self.table[sol.covered]["cost"] == cost:
                self.table[sol.covered]["sols"].append(sol)
                if len(self.table[sol.covered]["sols"]) > self.border:
                    to_rem = random.randint(0, len(self.table[sol.covered]["sols"]) - 1)
                    del self.table[sol.covered]["sols"][to_rem]
        except Exception as _:
            self.table[sol.covered] = {}
            self.table[sol.covered]["cost"] = sol.cost
            self.table[sol.covered]["sols"] = [sol]

    def non_dominated(self, sol):
        cost = sol.cost
        insert = False
        try:
            if self.table[sol.covered]["cost"] > cost:
                insert = True
            elif self.table[sol.covered]["cost"] == cost:
                insert = True
        except Exception as _:
            insert = True
        return insert

    def clean(self):
        '''
        cleans up the table after (not threadsafe should be run sequentially)
        '''
        keys = list(map(lambda x: int(x), self.table.keys()))
        last = max(keys)
        for i in reversed(range(0, max(keys))):
            in_square = floor((last - i) / self.epsilon) == 0
            try:
                if in_square and self.use_epsilon:
                    dist = self.table[i]["cost"] - self.table[last]["cost"] + last - i
                    if dist > 0:
                        del self.table[i]
                    else:
                        del self.table[last]
                        last = i
                elif self.table[last]["cost"] <= self.table[i]["cost"]:
                    del self.table[i]
                else:
                    last = i
            except Exception as _:
                pass
        self.key_gen = self.get_key_generator()

    def get_pop_chunk(self):
        return self.table[next(self.key_gen)]["sols"]

    def get_best(self):
        try:
            return self.table[self.to_be_covered]["sols"][0]
        except Exception as _:
            return sys.maxsize
