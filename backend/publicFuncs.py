from random import choice, sample
from src import Job, Machine, Solution
from reqs import machinability
from datetime import datetime
from copy import deepcopy
from random import choice, randint, random

#OK
def generateRandomSolution(jobs:list[Job], startDate:datetime, machineNames:list[str] = []) -> Solution:
    machineNames = machinability.keys() if not machineNames else machineNames
    sol = Solution([Machine(machineName, [], startDate) for machineName in machineNames])

    randJobs = sample(deepcopy(jobs), len(jobs))

    while len(randJobs) > 0:

        selectedMachine = choice(sol.machines)
        while not selectedMachine.machinability(randJobs[0]):
            selectedMachine = choice(sol.machines)
            if not any([mac.machinability(randJobs[0]) for mac in sol.machines]):
                raise RuntimeError(f"job cannot machinable any machine {randJobs[0].jobCode}")
                

        selectedJob = randJobs.pop(0)
        selectedMachine.jobSequence.append(selectedJob)
    
    sol.updateMachines()
    return sol


def generateRandomLocalSearchSolution(jobs:list[Job], startDate:datetime) -> Solution:
    sol = Solution([Machine(machineName, [], startDate) for machineName in machinability.keys()])

    randJobs = sample(deepcopy(jobs), len(jobs))

    while len(randJobs) > 0:
        selectedJob = randJobs.pop(0)
        print(len(randJobs))
        
        selectableMachines:list[Machine] = []
        for mac in sol.machines:
            if mac.machinability(selectedJob):
                selectableMachines.append(mac)
        if not selectableMachines: ValueError(f"job cannot machinable any machine {selectedJob.jobCode}")
        
        #LocalSearch
        bestSol = deepcopy(sol)
        bestSolObj = bestSol.getCmax()

        for macIndex, mac in enumerate(sol.machines):
            actSol = deepcopy(sol)
            actSol.machines[macIndex] = fitLocalJob2Machine(selectedJob, mac)
            actSol.updateMachines()
            
            if actSol.getCmax() < bestSolObj:
                bestSol = deepcopy(actSol)
                bestSolObj = bestSol.getCmax()

    bestSol.updateMachines()
    return bestSol


def fitJob2MachineLocalSearch4Cmax(job:Job, machine:Machine) -> Machine:
    bestMac = deepcopy(machine)
    actMac = deepcopy(machine)
    for index in range(len(machine.jobSequence) + 1):
        actMac = deepcopy(machine)
        actMac.jobSequence.insert(index, job)
        actMac.updateJobs()
        if actMac.getCmax() < bestMac.getCmax():
            bestMac = deepcopy(actMac)
    return bestMac


#aq iki kere çalıştırınca geliyor (constructiveHTest.ipynb'de)
def fitLocalJob2Machine(job:Job, machine:Machine) -> Machine:
    bestMac = deepcopy(machine)
    bestMac.jobSequence.append(job)
    bestMacObj = bestMac.getCmax()
    for index in range(len(machine.jobSequence) + 1):
        actMac = deepcopy(machine)
        actMac.jobSequence.insert(index, job)
        actMac.updateJobs()
        
        if actMac.getCmax() < bestMacObj:
            bestMac = deepcopy(actMac)
            bestMacObj = bestMac.getCmax()
    
    return bestMac


#OK
def generateNeighbor(sol:Solution) -> Solution:
    nghbr = deepcopy(sol)
    
    selectedMachine = choice([machine for machine in nghbr.machines if len(machine.jobSequence) > 0])
    selectedJob = selectedMachine.jobSequence.pop(randint(0,len(selectedMachine.jobSequence))-1)
    
    newSelectedMachine = choice(nghbr.machines)
    while not newSelectedMachine.machinability(selectedJob):
        newSelectedMachine = choice(nghbr.machines)
    
    newSelectedMachine.jobSequence.insert(randint(0,len(newSelectedMachine.jobSequence)), selectedJob)
    
    nghbr.updateMachines()
    return nghbr
"""
def generateNeighborLocalSearch(sol:Solution) -> Solution:
    nghbr = deepcopy(sol)
    
    selectedMachine = choice([machine for machine in nghbr.machines if len(machine.jobSequence) > 0])
    selectedJob = selectedMachine.jobSequence.pop(randint(0,len(selectedMachine.jobSequence))-1)
    
    newSelectedMachine = choice(nghbr.machines)
    while not newSelectedMachine.machinability(selectedJob):
        newSelectedMachine = choice(nghbr.machines)
    
    newSelectedMachine.jobSequence.insert(randint(0,len(newSelectedMachine.jobSequence)), selectedJob)
    
    nghbr.updateMachines()
    return nghbr
"""

def generateNeighbor4JobOrder(sol:Solution) -> Solution:
    nghbr = deepcopy(sol)
    
    selectedMachine = choice([machine for machine in nghbr.machines if len(machine.jobSequence) > 0])
    selectedJob = selectedMachine.jobSequence.pop(randint(0,len(selectedMachine.jobSequence))-1)
    
    newSelectedMachine = choice(nghbr.machines)
    while not newSelectedMachine.machinability(selectedJob):
        newSelectedMachine = choice(nghbr.machines)
    
    newSelectedMachine.jobSequence.append(selectedJob)
    
    nghbr.updateMachines()
    return nghbr


def generateNeighborAntiTardy(sol:Solution) -> Solution:
    nghbr = deepcopy(sol)
    
    #selection tardy machine
    tardyMachines:list[Machine] = [machine for machine in nghbr.machines if machine.getTardiness() > 0 and len(machine.jobSequence)>0]
    if len(tardyMachines) == 0: tardyMachines = nghbr.machines #if it isn't tardy, select randomly
    selectedMachine = choice(tardyMachines)
    while not selectedMachine:
        selectedMachine = choice(tardyMachines)
        
    
    #selection tardy job
    tardyJobs:list[Job] = []
    for job in selectedMachine.jobSequence:
        if job.dueDate < job.endDate:
            tardyJobs.append(job)
    if len(tardyJobs) == 0: tardyJobs = selectedMachine.jobSequence
    selectedJob = choice(tardyJobs)
    selectedMachine.jobSequence.remove(selectedJob)
    
    newSelectedMachine = choice(nghbr.machines)
    while not newSelectedMachine.machinability(selectedJob):
        newSelectedMachine = choice(nghbr.machines)
    
    newSelectedMachine.jobSequence.insert(randint(0,len(newSelectedMachine.jobSequence)),
                                          selectedJob)
    
    nghbr.updateMachines()
    return nghbr


def generateNeighborGroupOrder(sol:Solution) -> Solution:
    nghbr = deepcopy(sol)
    
    #machine selection
    selectedMachine = choice(nghbr.machines)
    while not selectedMachine.jobSequence:
        selectedMachine = choice(nghbr.machines)

    #job selection
    selectedJob = choice(selectedMachine.jobSequence)
    selectedJobIndex = selectedMachine.jobSequence.index(selectedJob)
    
    #group selection
    selectedGroup:list[Job] = []
    for job in selectedMachine.jobSequence[selectedJobIndex:]:
        if job.diameter != selectedJob.diameter: break
        selectedGroup.append(job)
        selectedMachine.jobSequence.remove(job)
    for job in selectedMachine.jobSequence[0:selectedJobIndex:-1]:
        if job.diameter != selectedJob.diameter: break
        selectedGroup.insert(0, job)
        selectedMachine.jobSequence.remove(job)
    
    newSelectedMachine = choice(nghbr.machines)
    while not any([newSelectedMachine.machinability(job) for job in selectedGroup]):
        newSelectedMachine = choice(nghbr.machines)
    
    newSelectedMachine.jobSequence += selectedGroup
    
    nghbr.updateMachines()
    return nghbr

def generateNeighborGroupOrderSmall2(sol:Solution) -> Solution:
    nghbr = deepcopy(sol)
    
    #machine selection
    selectedMachine = choice(nghbr.machines)
    while not selectedMachine.jobSequence:
        selectedMachine = choice(nghbr.machines)

    #job selection
    selectedJob = choice(selectedMachine.jobSequence)
    selectedJobIndex = selectedMachine.jobSequence.index(selectedJob)
    
    #group selection
    selectedGroup:list[Job] = []
    if random() > 0.5:
        for job in selectedMachine.jobSequence[selectedJobIndex:]:
            if job.diameter != selectedJob.diameter: break
            selectedGroup.append(job)
            selectedMachine.jobSequence.remove(job)
    else:
        for job in selectedMachine.jobSequence[-1:selectedJobIndex+1:-1]:
            if job.diameter != selectedJob.diameter: break
            selectedGroup.insert(0, job)
            selectedMachine.jobSequence.remove(job)
    
    newSelectedMachine = choice(nghbr.machines)
    while not any([newSelectedMachine.machinability(job) for job in selectedGroup]):
        newSelectedMachine = choice(nghbr.machines)
    
    newSelectedMachine.jobSequence += selectedGroup
    
    nghbr.updateMachines()
    return nghbr

def generateNeighborGroupOrder2(sol:Solution) -> Solution:
    nghbr = deepcopy(sol)
    
    #machine selection
    selectedMachine = choice(nghbr.machines)
    while not selectedMachine.jobSequence:
        selectedMachine = choice(nghbr.machines)

    #job selection
    selectedJob = choice(selectedMachine.jobSequence)
    selectedJobIndex = selectedMachine.jobSequence.index(selectedJob)
    
    #group selection
    selectedGroup:list[Job] = []
    for job in selectedMachine.jobSequence[selectedJobIndex:]:
        if job.diameter != selectedJob.diameter: break
        selectedGroup.append(job)
        selectedMachine.jobSequence.remove(job)
    for job in selectedMachine.jobSequence[0:selectedJobIndex:-1]:
        if job.diameter != selectedJob.diameter: break
        selectedGroup.insert(0, job)
        selectedMachine.jobSequence.remove(job)
    
    newSelectedMachine = choice(nghbr.machines)
    while not any([newSelectedMachine.machinability(job) for job in selectedGroup]):
        newSelectedMachine = choice(nghbr.machines)
    
    #newSelectedMachine.jobSequence.insert(randint(0,len(newSelectedMachine.jobSequence)),
    #                                     selectedJob)
    selectedInsertIndex = randint(0,len(newSelectedMachine.jobSequence))
    newSelectedMachine.jobSequence = newSelectedMachine.jobSequence[0: selectedInsertIndex
    ] + selectedGroup + newSelectedMachine.jobSequence[selectedInsertIndex:]
    
    nghbr.updateMachines()
    return nghbr


def generateNeighborGroupOrderSmall(sol:Solution) -> Solution:
    nghbr = deepcopy(sol)
    
    #machine selection
    selectedMachine = choice(nghbr.machines)
    while not selectedMachine.jobSequence:
        selectedMachine = choice(nghbr.machines)

    #job selection
    selectedJob = choice(selectedMachine.jobSequence)
    selectedJobIndex = selectedMachine.jobSequence.index(selectedJob)
    
    selectedGroup:list[Job] = []
    #group selection
    if choice([True, False]):
        for job in selectedMachine.jobSequence[selectedJobIndex:]:
            if job.diameter != selectedJob.diameter: break
            selectedGroup.append(job)
            selectedMachine.jobSequence.remove(job)
    else:
        for job in selectedMachine.jobSequence[0:selectedJobIndex:-1]:
            if job.diameter != selectedJob.diameter: break
            selectedGroup.insert(0, job)
            selectedMachine.jobSequence.remove(job)
    
    newSelectedMachine = choice(nghbr.machines)
    while not any([newSelectedMachine.machinability(job) for job in selectedGroup]):
        newSelectedMachine = choice(nghbr.machines)
    
    #newSelectedMachine.jobSequence.insert(randint(0,len(newSelectedMachine.jobSequence)),
    #                                      selectedJob)
    
    
    selectedInsertIndex = randint(0,len(newSelectedMachine.jobSequence))
    newSelectedMachine.jobSequence = newSelectedMachine.jobSequence[0: selectedInsertIndex
    ] + selectedGroup + newSelectedMachine.jobSequence[selectedInsertIndex:]
    
    nghbr.updateMachines()
    return nghbr


def generateNeighborGroupOrderSmallLocalSearch(sol:Solution) -> Solution:
    nghbr = deepcopy(sol)
    
    #machine selection
    selectedMachine = choice(nghbr.machines)
    while not selectedMachine.jobSequence:
        selectedMachine = choice(nghbr.machines)

    #job selection
    selectedJob = choice(selectedMachine.jobSequence)
    selectedJobIndex = selectedMachine.jobSequence.index(selectedJob)
    
    selectedGroup:list[Job] = []
    #group selection
    if choice([True, False]):
        for job in selectedMachine.jobSequence[selectedJobIndex:]:
            if job.diameter != selectedJob.diameter: break
            selectedGroup.append(job)
            selectedMachine.jobSequence.remove(job)
    else:
        for job in selectedMachine.jobSequence[0:selectedJobIndex:-1]:
            if job.diameter != selectedJob.diameter: break
            selectedGroup.insert(0, job)
            selectedMachine.jobSequence.remove(job)
    
    newSelectedMachine = choice(nghbr.machines)
    while not any([newSelectedMachine.machinability(job) for job in selectedGroup]):
        newSelectedMachine = choice(nghbr.machines)
    
    #LOCAL SEARCH
    bestGroup = deepcopy(newSelectedMachine)
    for index in range(len(newSelectedMachine.jobSequence)):
        newSelectedMachineCopy = deepcopy(newSelectedMachine)
        newSelectedMachineCopy.jobSequence = newSelectedMachineCopy.jobSequence[0:index] + selectedGroup + newSelectedMachineCopy.jobSequence[index:]
        newSelectedMachineCopy.updateJobs()
        if newSelectedMachineCopy.getCmax() < bestGroup.getCmax():
            bestGroup = deepcopy(newSelectedMachineCopy)
        print(index)
    print("gotcha")
    newSelectedMachine = bestGroup
    
    nghbr.updateMachines()
    return nghbr




def solution2Char(sol:Solution) -> str:
    totalStr = ""
    for machine in sol.machines:
        totalStr += machine.machineName
        for job in machine.jobSequence:
            totalStr += job.jobCode
    return totalStr


def solutionInfo(sol:Solution):
    print("\n . . . : : : SOLUTION INFO : : : . . . ")
    print(f"Objective Func = {sol.objFunc()}")
    print(f"Tardiness: {sol.getTardiness():.5f}\tCmax: {sol.getCmaxReal():.5f}")
    
    print("\nMACHINE\t   Tardiness\t  Cmax ")
    for machine in sol.machines:
        print(f"{machine.machineName}\t = {machine.getTardiness():.5f} \t| {machine.getCmaxReal():.5f}")



def solution2json(solution:Solution, timeUpscale:float=5.0) -> dict:
    data = {}
    for machine in solution.machines:
        data_row = []
        for job in machine.jobSequence:
            data_row.append((f"{job.diameter}X{job.length}-{job.standart}-{job.quality}", job.runTime * timeUpscale, 20, job.jobIndex))
            #data_row.append((job.jobCode, job.runTime * timeUpscale, 20))
        data[machine.machineName] = data_row
        #data[machine.machineName+"StartDate"] = machine.startDate
        
    return data