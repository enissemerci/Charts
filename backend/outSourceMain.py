import pandas
from src import Job, Solution, Machine
from datetime import datetime
import publicFuncs
import metaheuristics


"""
PREFORMANCE TESTING
"""


#data = pandas.read_excel("plan_data.xlsx", "Soğuk Dövme")
data = pandas.read_excel("Üretim Planı 14-21.09.XLSX", "Soğuk Dövme")
startDate = datetime.strptime("14/09/2023", "%d/%m/%Y")

#data = pandas.read_excel("macjob8-6.xlsx", "3 machine 8 jobs")
#startDate = datetime.strptime("08/08/2023", "%d/%m/%Y")

import reqs
reqs.loadData(data=data, startDate=startDate)

machineNames = reqs.machinability.keys()
#machineNames = ["415", "416", "518"]


ustaSol = Solution([Machine(machineName, [], startDate) for machineName in machineNames])
#jobs = [Job(index, data.iloc[index], startDate", "%d/%m/%Y")) for index in range(len(data))]
jobs = [Job(index, data.iloc[index], startDate) for index in range(len(data))]

counter = 0
for machine in ustaSol.machines:
    for job in jobs:
        if machine.machineName == job.assignedMachineName:
            if machine.machinability(job):
                machine.jobSequence.append(job)
                counter += 1
            else: 
                print(" UNMACHINABLE JOB FOUND and REMOVED", machine.machineName,  job.jobIndex, job.jobCode)
                jobs.remove(job)
ustaSol.updateMachines()


print(counter, " jobs added")

publicFuncs.solutionInfo(ustaSol)

jobs = [Job(index, data.iloc[index], startDate) for index in range(len(data))]
startSol = publicFuncs.generateRandomSolution(jobs, startDate, machineNames)

from copy import deepcopy
finalSol = deepcopy(startSol)

finalSol.solutionInfo()



print(finalSol.objFunc())
#finalSol = metaheuristics.jobOrderSequence(finalSol)
print(finalSol.objFunc())

print("#"*50)

finalSol = metaheuristics.simulatedAnnealing(finalSol, tStart=100, tEnd=0.1 ,alpha=0.99, markov=100,
                                             nghbrFunc=publicFuncs.generateNeighbor)


finalSol.updateMachines()
publicFuncs.solutionInfo(finalSol)







"""

import numpy as np
from metaheuristics import simulated_annealing_gpu


# Example usage
initial_solution_data = np.array([1.0, 2.0, 3.0]).astype(np.float32)
final_solution_data = simulated_annealing_gpu(initial_solution_data, t_start=0.1, t_end=0.001, alpha=0.95, markov=50)
print("Final solution:", final_solution_data)

"""