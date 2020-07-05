import json
import time
import multiprocessing
import numpy as np
import sys
import os
try:
    from source.beasley_reader import BeasleyReader
    from source.mylogging import Logging
    from source.set_cover import SetCover
    from source.GCAIS import *
    from source.GSEMO import *
    from source.excel_reader import *
except Exception as _:
    from beasley_reader import BeasleyReader
    from mylogging import Logging
    from set_cover import SetCover
    from GCAIS import *
    from GSEMO import *
    from excel_reader import *

# GLOBAL
PROCESSES = 4
ITERATIONS = 100

ALGO_ITER = 1500000

# GCAIS parameters
GCAIS_ITERATIONS = ALGO_ITER

# GSEMO
GSEMO_ITERATIONS = ALGO_ITER
LOCAL_POPULATIONS = 30

ALGORITHMS = [
              lambda sci: GCAIS_BASE(sci, 2000),
              lambda sci: Simple_GSEMO(sci, 30, 20000),
              lambda sci: EpsilonGCAIS(sci, 2000, 5),
              lambda sci: EpsilonGCAIS(sci, 2000, 10),
              lambda sci: EpsilonGCAIS(sci, 2000, 15),
              lambda sci: EpsilonBoundedGCAIS(sci, 2000, 200, -1),
              lambda sci: EpsilonBoundedGCAIS(sci, 2000, 200, 5),
              lambda sci: EpsilonBoundedGCAIS(sci, 2000, 200, 10),
              lambda sci: EpsilonBoundedGCAIS(sci, 2000, 200, 15)
              ]

def prepare_data(path):
    file = open(path)
    data = json.load(file)
    problem_matrix = np.array(data)
    return SetCover(problem_matrix)


PROBLEM_INSTANCES = {}
# 0 for Beasley, 1 for industrial data
MODE = 1
SIMULATED_DATASETS = 4
SIMULATED_BAD_CASES = 5
SIMULATED_MAX_K = 5
SIMULATED_N = 5

if MODE == 0:
    filez = list(filter(lambda x: ".txt" in x, os.listdir("DATA")))
    filez = list(filter(lambda x: "scpe" in x, filez))
    for file in filez:
        prob_path = "DATA" + os.sep + file
        prob_instance = BeasleyReader(prob_path).read_file()
        name = file[:-4] + ".json"
        PROBLEM_INSTANCES["DATA" + os.sep + name] = prob_instance
if MODE == 1:
    polarions = ["fridge1.xlsx", "fridge2.xlsx"]
    for polarion in polarions:
        prob_path = "DATA" + os.sep + polarion
        prob_instance = SetCover(PolarionReader(prob_path).create_np_matrix())
        name = polarion[:-5] + ".json"
        PROBLEM_INSTANCES["DATA" + os.sep + name] = prob_instance


#def has_converged(found, current):
#    assert current - found > 0
#    if current - found > 100:
#        return True
#    return False


def iter_problem(problem_instance, iteration, name):
    results = {}
    runtime_results = {}
    for alg_creator in ALGORITHMS:
        algo = alg_creator(problem_instance)
        loc_name = "FINE_RESULTS" + os.sep + name.split(os.sep)[-1][:-5] + "_" + algo.name + "_" + str(iteration) + ".json"
        logger = Logging(loc_name)
        algo.set_logging(logger)
        start = time.time()
        approx = algo.find_approximation()
        try:
            results[algo.name] = approx.cost
        except Exception as _:
            results[algo.name] = approx
        end = time.time()
        duration = float(end - start)
        runtime_results[algo.name] = duration
        logger.save()
    name = "RESULTS" + os.sep + name.split(os.sep)[-1][:-5] + "_" + str(iteration) + ".json"
    with open(name, "w") as file:
        json.dump(results, file, sort_keys=True, indent=4)
    name = "RUNTIME_RESULTS" + os.sep + name.split(os.sep)[-1][:-5] + "_" + str(iteration) + ".json"
    with open(name, "w") as file:
        json.dump(runtime_results, file, sort_keys=True, indent=4)


def experiment_iter(iteration):
    global PROBLEM_INSTANCES
    for problem in PROBLEM_INSTANCES.keys():
        iter_problem(PROBLEM_INSTANCES[problem], iteration, problem)


def start_experiments(exp_fun, parallel):
    if parallel:
        p = multiprocessing.Pool(PROCESSES)
        avg_res = p.map(exp_fun, range(ITERATIONS))
    else:
        for i in range(0, ITERATIONS):
            exp_fun(i)


def run_set_cover_experiment(parallel=True):
    start_experiments(experiment_iter, parallel)


if __name__ == '__main__':
    run_set_cover_experiment(False)
