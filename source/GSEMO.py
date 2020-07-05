try:
    from source.set_cover import *
except Exception as _:
    from set_cover import *
import numpy as np
import copy
import random
import sys
import time


class Simple_GSEMO:

    def __init__(self, problem_instance, loc_pops, iterations):
        self.name = "SIMPLE_GSEMO"
        self.populations = []
        self.problem = problem_instance
        self.iterations = iterations
        self.pops = loc_pops
        prob_shape = self.problem.problem_instance.shape
        self.send_prob = loc_pops / (prob_shape[0] * prob_shape[1])
        number_of_sets = self.problem.problem_instance.shape[0]
        for _ in range(0, loc_pops):
            sol_vector = np.zeros(number_of_sets)
            population = [Solution(self.problem, sol_vector)]
            self.populations.append(population)
        self.iter = 0

    def superior(self, sol_a, sol_b):
        if sol_a.cost <= sol_b.cost:
            if sum(sol_a.covered_elements) > sum(sol_b.covered_elements):
                return True
        if sum(sol_a.covered_elements) >= sum(sol_b.covered_elements):
            if sol_a.cost < sol_b.cost:
                return True
        return False

    def mutate(self, sol):
        mut_prob = 1.0 / len(sol.set_vector)
        new_sol = copy.deepcopy(sol.set_vector)
        for i in range(0, len(sol.set_vector)):
            if random.random() < mut_prob:
                new_sol[i] = 1 if new_sol[i] == 0 else 0
        return Solution(self.problem, new_sol)

    def rand_choice(self, pop):
        i = random.randint(0, len(pop) - 1)
        return pop[i]

    def insert_to_pop(self, ele, pop):
        for other in pop:
            if self.superior(other, ele):
                return False
        pop.append(ele)
        return True

    def iteration(self):
        for pop in self.populations:
            ele = self.rand_choice(pop)
            mutated = self.mutate(ele)
            inserted = self.insert_to_pop(mutated, pop)
            if inserted:
                if random.random() < self.send_prob:
                    for other_pop in self.populations:
                        self.insert_to_pop(mutated, other_pop)
        self.iter = self.iter + 1

    def set_logging(self, logger):
        self.logger = logger

    def get_population_size(self):
        size = 0
        for pop in self.populations:
            size += len(pop)
        return size

    def find_approximation(self):
        print("start GSEMO")
        found = 0
        old_best = sys.maxsize
        s = time.time()
        for i in range(0, self.iterations):
            if i % 10 == 0:
                print_now()
                print("finished " + str(i / self.iterations) + " percent of GSEMO")
            iter_start = time.time()
            try:
                self.iteration()
            except Exception as _:
                break
            iter_end = time.time()
            feasible = []
            for pop in self.populations:
                feasible.extend(list(filter(lambda x: x.is_feasible, pop)))
            try:
                best = min(feasible, key=lambda x: x.cost).cost
            except Exception as e:
                best = sys.maxsize
            if best != sys.maxsize:
                if best < old_best:
                    found = i
                    old_best = best
                elif has_converged(found, i, time.time() - s):
                    break
            self.logger.log_entry(self.iter, best, float(iter_end - iter_start), self.get_population_size())
        feasible = []
        for pop in self.populations:
            feasible.extend(list(filter(lambda x: x.is_feasible, pop)))
        if len(feasible) == 0:
            all_sets = np.ones(self.problem.problem_instance.shape[0])
            return Solution(self.problem, all_sets)
        print("finished GSEMO")
        return min(feasible, key=lambda x: x.cost)

