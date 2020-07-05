import numpy as np
import sys
import random
import itertools
from datetime import datetime

def has_converged(found, current, duration):
    #assert current - found > 0
    #assert duration > 0
    #print(duration)
    if current - found > 100:
        return True
    if duration > 200:
        return True
    return False

def print_now():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)

class SetCover:
    '''
    Represents an instance of the Minimum Set Cover problem
    '''
    def __init__(self, problem_instance):
        '''
        :param problem_instance: two dimensional numpy array. The rows represent the available
        sets and the columns the possible elements. If problem_instance[i][j] is one then i-th
        set has the j-th element. If it is set to 0 then the set does not have this element.
        '''
        self.problem_instance = problem_instance
        self.is_solveable()

    def is_solveable(self):
        '''
        Checks if there exists a set cover at all. Raises an Exception if not.
        '''
        all_sets = np.ones(self.problem_instance.shape[0])
        solution = Solution(self, all_sets)
        if not solution.is_feasible_solution():
            raise Exception("Set cover instance cannot be solved")


class Solution:
    '''
    Represents a possible infeasible solution of the Set Cover problem
    '''
    def __init__(self, set_cover_instance, set_vector, is_feasible=None, cost=None):
        '''
        :param set_cover_instance: instance of SetCover
        :param set_vector: numpy vector indicating the sets that the solution holds.
        The i-th entry of set_vector corresponds to the i-th row of the set cover
        table.
        :param is_feasible: indicates if the solution is a possible set cover.
        :param cost: number of sets in the cover.
        '''
        self.set_cover_instance = set_cover_instance
        self.set_vector = set_vector
        self.is_feasible = is_feasible
        self.cost = cost
        self.is_feasible_solution()

    def equals_other_sol(self, other_sol):
        for i in range(0, len(self.set_vector)):
            if self.set_vector[i] != other_sol.set_vector[i]:
                return False
        return True

    def add_set(self, index):
        '''
        Adds the set of the given index to the solution. Afterwards the cost is updated
        and is checked if the solution becomes feasible.

        :param index: index in the set cover table of the set.
        '''
        if self.set_vector[index] == 1:
            return False
        self.set_vector[index] = 1
        self.cost += 1
        self.covered_elements += self.set_cover_instance.problem_instance[index]
        self.covered_elements = [1 if ele > 0 else 0 for ele in self.covered_elements]
        if sum(self.covered_elements) == self.set_cover_instance.problem_instance.shape[1]:
            self.is_feasible = True
        self.covered = sum(self.covered_elements)
        return True

    def get_cost(self):
        if self.is_feasible():
            return self.cost
        else:
            return sys.maxsize

    def is_feasible_solution(self):
        '''
        Also retrieves the covered elements and calculates the solutions cost.
        '''
        if self.is_feasible is not None:
            return self.is_feasible
        available_elements = np.zeros(len(self.set_cover_instance.problem_instance[0]))
        cost = 0
        for i in range(0, len(self.set_vector)):
            if self.set_vector[i] == 1:
                cost += 1
                available_elements += self.set_cover_instance.problem_instance[i]
        self.covered_elements = [1 if ele > 0 else 0 for ele in available_elements]
        self.covered = sum(self.covered_elements)
        if len(available_elements[0 in available_elements]) == 0:
            self.cost = cost
            self.is_feasible = True
            return self.is_feasible
        self.cost = cost
        self.is_feasible = False
        return self.is_feasible
