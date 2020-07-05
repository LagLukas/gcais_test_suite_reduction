try:
    from source.set_cover import *
    from source.gcais_population import GCAISPopulation
except Exception as _:
    from set_cover import *
    from gcais_population import GCAISPopulation
import numpy as np
import copy
import random
import sys
import time
from math import floor

class EpsilonGCAIS:

    def __init__(self, problem_instance, iterations, epsilon):
        val_epsilon = str(epsilon) if epsilon > 0 else "no_epsilon"
        self.name = "eGCAIS" + "_" + val_epsilon
        self.problem_instance = problem_instance
        self.iterations = iterations
        self.epsilon = epsilon
        number_of_sets = self.problem_instance.problem_instance.shape[0]
        sol_vector = np.ones(number_of_sets)
        self.population = [Solution(self.problem_instance, sol_vector)]
        self.iter = 0

    def superior(self, sol_a, sol_b):
        if sol_a.cost <= sol_b.cost:
            if sol_a.covered > sol_b.covered:
                return True
        if sol_a.covered >= sol_b.covered:
            if sol_a.cost < sol_b.cost:
                return True
        return False

    def dominated_by_any(self, sol_set, ele):
        for solution in sol_set:
            in_square = (abs(floor((solution.covered - ele.covered)) / self.epsilon) == 0)
            in_square = in_square and (abs(floor((solution.cost - ele.cost)) / self.epsilon) == 0)
            if in_square:
                dist = ele.cost - solution.cost + solution.covered - ele.covered
                if dist > 0:
                    return True
                else:
                    return False
            elif self.superior(solution, ele):
                return True
        return False

    def mutate(self, sol):
        mut_prob = 1.0 / len(sol.set_vector)
        new_sol = copy.deepcopy(sol.set_vector)
        for i in range(0, len(sol.set_vector)):
            if random.random() < mut_prob:
                new_sol[i] = 1 if new_sol[i] == 0 else 0
        return Solution(self.problem_instance, new_sol)

    def iteration(self):
        mutated_pop = list(map(lambda x: self.mutate(x), self.population))
        mutated_pop = list(filter(lambda x: not self.dominated_by_any(self.population, x), mutated_pop))
        self.population = list(filter(lambda x: not self.dominated_by_any(mutated_pop, x), self.population))
        self.population.extend(mutated_pop)
        self.iter = self.iter + 1

    def set_logging(self, logger):
        self.logger = logger

    def find_approximation(self):
        print("start base eGCAIS")
        old_best = sys.maxsize
        found = 0
        s = time.time()
        for i in range(0, self.iterations):
            if i % 10 == 0:
                print_now()
                print("finished " + str(i / self.iterations) + " percent of base eGCAIS")
            iter_start = time.time()
            try:
                self.iteration()
            except Exception as _:
                # yikes memory error
                break
            iter_end = time.time()
            feasible = list(filter(lambda x: x.is_feasible, self.population))
            try:
                best = min(feasible, key=lambda x: x.cost).cost
            except Exception as e:
                best = sys.maxsize
            if best != sys.maxsize:
                if best < old_best:
                    found = self.iter
                    old_best = best
            if has_converged(found, self.iter, time.time() - s):
                break
            self.logger.log_entry(self.iter, best, float(iter_end - iter_start), len(self.population))
        feasible = list(filter(lambda x: x.is_feasible, self.population))
        if len(feasible) == 0:
            all_sets = np.ones(self.problem_instance.problem_instance.shape[0])
            return Solution(self.problem_instance, all_sets)
        print("finished base eGCAIS")
        return min(feasible, key=lambda x: x.cost)


class EpsilonBoundedGCAIS:

    def __init__(self, problem_instance, iterations, border, epsilon):
        val_border = str(border) if border != sys.maxsize else "no_border"
        val_epsilon = str(epsilon) if epsilon > 0 else "no_epsilon"
        self.name = "ebGCAIS" + "_" + val_border + "_" + val_epsilon
        self.problem_instance = problem_instance
        self.iterations = iterations
        self.border = border
        self.epsilon = epsilon
        to_be_covered = self.problem_instance.problem_instance.shape[1]
        number_of_sets = self.problem_instance.problem_instance.shape[0]
        sol_vector = np.ones(number_of_sets)
        initial_sol = Solution(self.problem_instance, sol_vector)
        self.population = GCAISPopulation(initial_sol, to_be_covered, border, epsilon, epsilon > 0)
        self.iter = 0

    def mutate(self, sol):
        mut_prob = 1.0 / len(sol.set_vector)
        new_sol = copy.deepcopy(sol.set_vector)
        for i in range(0, len(sol.set_vector)):
            if random.random() < mut_prob:
                new_sol[i] = 1 if new_sol[i] == 0 else 0
        return Solution(self.problem_instance, new_sol)

    def mutate_and_insert(self):
        mutated = []
        for key in self.population.table.keys():
            chunk = self.population.table[key]["sols"]
            mutated.append(list(map(lambda x: self.mutate(x), chunk)))
        for mutations in mutated:
            for mutated in mutations:
                self.population.try_insert(mutated)

    def iteration(self):
        self.mutate_and_insert()
        self.population.clean()
        self.iter = self.iter + 1

    def set_logging(self, logger):
        self.logger = logger

    def find_approximation(self):
        print("start epsilon bounded GCAIS")
        old_best = sys.maxsize
        found = 0
        s = time.time()
        for i in range(0, self.iterations):
            if i % 10 == 0:
                print_now()
                print("finished " + str(i / self.iterations) + " percent of epsilon bounded GCAIS")
            iter_start = time.time()
            self.iteration()
            iter_end = time.time()
            try:
                best = self.population.get_best().cost
            except Exception as _:
                best = sys.maxsize
            if best != sys.maxsize:
                if best < old_best:
                    found = self.iter
                    old_best = best
                else:
                    if has_converged(found, self.iter, time.time() - s):
                        break
            self.logger.log_entry(self.iter, best, float(iter_end - iter_start), self.population.get_population_size())
        print("finished epsilon bounded GCAIS")
        return self.population.get_best()


class GCAIS_BASE:

    def __init__(self, problem_instance, iterations):
        self.name = "GCAIS_BASE"
        self.population = {}
        self.problem_instance = problem_instance
        self.iterations = iterations
        number_of_sets = self.problem_instance.problem_instance.shape[0]
        sol_vector = np.ones(number_of_sets)
        self.population = [Solution(self.problem_instance, sol_vector)]
        self.iter = 0

    def superior(self, sol_a, sol_b):
        if sol_a.cost <= sol_b.cost:
            if sol_a.covered > sol_b.covered:
                return True
        if sol_a.covered >= sol_b.covered:
            if sol_a.cost < sol_b.cost:
                return True
        return False

    def dominated_by_any(self, sol_set, ele):
        for solution in sol_set:
            if self.superior(solution, ele):
                return True
        return False

    def mutate(self, sol):
        mut_prob = 1.0 / len(sol.set_vector)
        new_sol = copy.deepcopy(sol.set_vector)
        for i in range(0, len(sol.set_vector)):
            if random.random() < mut_prob:
                new_sol[i] = 1 if new_sol[i] == 0 else 0
        return Solution(self.problem_instance, new_sol)

    def iteration(self):
        mutated_pop = list(map(lambda x: self.mutate(x), self.population))
        mutated_pop = list(filter(lambda x: not self.dominated_by_any(self.population, x), mutated_pop))
        self.population = list(filter(lambda x: not self.dominated_by_any(mutated_pop, x), self.population))
        self.population.extend(mutated_pop)
        self.iter = self.iter + 1

    def set_logging(self, logger):
        self.logger = logger

    def find_approximation(self):
        print("start base GCAIS")
        old_best = sys.maxsize
        found = 0
        s = time.time()
        for i in range(0, self.iterations):
            if i % 10 == 0:
                print_now()
                print("finished " + str(i / self.iterations) + " percent of base GCAIS")
            iter_start = time.time()
            self.iteration()
            iter_end = time.time()
            feasible = list(filter(lambda x: x.is_feasible, self.population))
            try:
                best = min(feasible, key=lambda x: x.cost).cost
            except Exception as e:
                best = sys.maxsize
            if best != sys.maxsize:
                if best < old_best:
                    found = self.iter
                    old_best = best
                else:
                    if has_converged(found, self.iter, time.time() - s):
                        break
            self.logger.log_entry(self.iter, best, float(iter_end - iter_start), len(self.population))
        feasible = list(filter(lambda x: x.is_feasible, self.population))
        if len(feasible) == 0:
            all_sets = np.ones(self.problem_instance.problem_instance.shape[0])
            return Solution(self.problem_instance, all_sets)
        print("finished base GCAIS")
        return min(feasible, key=lambda x: x.cost)
