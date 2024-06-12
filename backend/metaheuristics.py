from src import Solution, Job
from publicFuncs import generateNeighbor, solution2Char
from copy import deepcopy
from time import time
from math import e, pow
from random import random

def tabu(
    startSol:Solution,
    timeLimit:int=120,
    nghbrFunc=generateNeighbor,
    neighborSize:int=50,
    ) -> Solution:

    tabuList = []
    actSol = deepcopy(startSol)
    bestSol = deepcopy(startSol)
    bestObj = bestSol.objFunc()
    
    startTime = time()
    elapsedTime = time() - startTime
    
    while elapsedTime < timeLimit:
        elapsedTime = time() - startTime
    
        nghbrs:Solution = []
        for _ in range(neighborSize):
            newSol:Solution = nghbrFunc(actSol)
            newSol.updateMachines()
            while solution2Char(newSol) in tabuList:
                newSol = nghbrFunc(actSol)
                
            nghbrs.append(newSol)
        
        actSol:Solution = min(nghbrs, key= lambda sol: sol.objFunc())
        tabuList.append(solution2Char(actSol))
        
        if actSol.objFunc() < bestSol.objFunc():
            bestSol = actSol
            bestObj = bestSol.objFunc()
            
        print(f"Tabu time:{elapsedTime:.3f} | best:{bestObj:.7f}")

    return bestSol


def simulatedAnnealing(startSol:Solution,
                       tStart:int = 0.1,
                       tEnd:int = 0.001,
                       alpha:float = 0.95,
                       markov:int = 50,
                       nghbrFunc=generateNeighbor,
                       objFuncCmaxSum=0.01,
                       graphData:bool=False) -> Solution:


    bestSol = startSol
    bestObj = bestSol.objFunc(cmax_sum=objFuncCmaxSum)

    actSol = deepcopy(startSol)
    actObj = actSol.objFunc(cmax_sum=objFuncCmaxSum)
    
    objData:list = []
    timeData:list = []
    startTime = time()

    temp = float(tStart)
    while temp > tEnd:
        for _ in range(markov):
            neighborSol:Solution = nghbrFunc(actSol)
            neighborSol.updateMachines()

            delta = neighborSol.objFunc(cmax_sum=objFuncCmaxSum) - actObj
            if delta < 0 or pow(e, -delta/temp) > random():
                actSol = neighborSol
                actObj = actSol.objFunc(cmax_sum=objFuncCmaxSum)

                if actObj < bestObj:
                    bestSol = actSol
                    bestObj = bestSol.objFunc(cmax_sum=objFuncCmaxSum)

        print(f"Sim.An. temp:{temp:.5f} act:{actObj:.5f} | best:{bestObj:.5f}")
        temp *= alpha
        if graphData: objData.append(bestObj); timeData.append(time()-startTime)
    return (bestSol, (timeData, objData)) if graphData else bestSol










"""

import numpy as np
import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
from copy import deepcopy

# Define Solution class with objFunc() and updateMachines() methods
class Solution:
    def __init__(self, data):
        self.data = data  # Placeholder for solution data (e.g., machine assignments)

    def objFunc(self):
        # Example objective function (sum of solution data)
        return np.sum(self.data)

    def updateMachines(self):
        # Example method to update solution data (can be customized)
        self.data += np.random.randint(-1, 2, size=self.data.shape)


"""



# CUDA kernel for neighbor generation and objective function evaluation in parallel
cuda_kernel = """
#include <math.h>
#include <curand_kernel.h>

__global__ void evaluate_neighbors(float *current_data, float *neighbor_data,
                                   int size, float *current_energy, float *neighbor_energy,
                                   float temp, float *rand_vals) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < size) {
        // Generate random perturbation for neighbor
        neighbor_data[idx] = current_data[idx] + rand_vals[idx];
        
        // Evaluate objective function for current and neighbor solutions
        current_energy[idx] = current_data[idx];  // Example: objFunc(current_data)
        neighbor_energy[idx] = neighbor_data[idx];  // Example: objFunc(neighbor_data)
    }
}
"""





"""

def simulated_annealing_gpu(start_sol_data, t_start=0.1, t_end=0.001, alpha=0.95, markov=50):
    # Compile CUDA kernel
    mod = SourceModule(cuda_kernel)
    evaluate_neighbors_kernel = mod.get_function("evaluate_neighbors")
    
    
    best_sol_data = np.copy(start_sol_data)
    best_obj = np.sum(best_sol_data)

    current_sol_data = np.copy(start_sol_data)
    current_obj = np.sum(current_sol_data)

    temp = float(t_start)
    size = len(start_sol_data)

    # Allocate GPU memory
    current_data_gpu = cuda.mem_alloc(current_sol_data.nbytes)
    neighbor_data_gpu = cuda.mem_alloc(current_sol_data.nbytes)
    current_energy_gpu = cuda.mem_alloc(current_sol_data.nbytes)
    neighbor_energy_gpu = cuda.mem_alloc(current_sol_data.nbytes)
    rand_vals_gpu = cuda.mem_alloc(current_sol_data.nbytes * 4)  # For random perturbations

    # Copy initial solution data to GPU memory
    cuda.memcpy_htod(current_data_gpu, current_sol_data)

    block_size = 256
    grid_size = (size + block_size - 1) // block_size

    rand_vals = np.random.uniform(-1, 1, size=size).astype(np.float32)
    cuda.memcpy_htod(rand_vals_gpu, rand_vals)

    while temp > t_end:
        for _ in range(markov):
            # Evaluate neighbors and objective functions in parallel on GPU
            evaluate_neighbors_kernel(current_data_gpu, neighbor_data_gpu,
                                      np.int32(size), current_energy_gpu, neighbor_energy_gpu,
                                      np.float32(temp), rand_vals_gpu,
                                      block=(block_size, 1, 1), grid=(grid_size, 1))

            # Copy energy values from GPU to CPU
            current_energy = np.empty_like(current_sol_data)
            neighbor_energy = np.empty_like(current_sol_data)
            cuda.memcpy_dtoh(current_energy, current_energy_gpu)
            cuda.memcpy_dtoh(neighbor_energy, neighbor_energy_gpu)

            # Acceptance criterion (Metropolis-Hastings)
            deltas = neighbor_energy - current_energy
            accept_mask = (deltas < 0) | (np.exp(-deltas / temp) > np.random.rand(size))
            current_sol_data[accept_mask] = neighbor_data_gpu.get()[accept_mask]
            current_obj = np.sum(current_sol_data)

            # Update best solution if current is better
            if current_obj < best_obj:
                best_sol_data[:] = current_sol_data[:]
                best_obj = current_obj

        print(f"Sim.An. temp: {temp:.5f} | act: {current_obj:.5f} | best: {best_obj:.5f}")
        temp *= alpha

    return best_sol_data


"""









"""
def jobOrderSequence(sol:Solution) -> Solution:
    newSol = deepcopy(sol)
    for machine in newSol.machines:
        machine.jobSequence = sorted(machine.jobSequence, 
                                     key= lambda job: (job.diameter,
                                                       job.standart,
                                                       job.quality,
                                                       job.length))
    newSol.updateMachines()
    return newSol

"""
def jobOrderSequence(sol:Solution) -> Solution:
    def quality(job:Job) -> int:
        jobQual = job.quality
        if jobQual in ["5.6", "5.8", "6.8", "4.6"]: return 0
        if jobQual in ["8.8"]: return 1
        if jobQual in ["10.8"]: return 2
        else: return 3
    def standart(job:Job) -> int:
        jobStan = job.standart
        if any(stan1 in jobStan for stan1 in ["933", "931"]): return 0
        if any(stan2 in jobStan for stan2 in ["7990", "4017", "4014"]): return 1
        else: return 2
    
    newSol = deepcopy(sol)
    for machine in newSol.machines:
        machine.jobSequence = sorted(machine.jobSequence, 
                                     key= lambda job: (job.diameter,
                                                       standart(job),
                                                       quality(job),
                                                       job.length))
    newSol.updateMachines()
    return newSol



def jobOrderSA(startSol:Solution,
                       tStart:int = 1000,
                       tEnd:int = 0.01,
                       alpha:float = 0.95,
                       markov:int = 20,
                       nghbrFunc=generateNeighbor) -> Solution:


    bestSol = startSol
    bestObj = bestSol.objFunc()

    actSol = deepcopy(startSol)
    actObj = actSol.objFunc()

    temp = float(tStart)
    while temp > tEnd:
        for _ in range(markov):
            neighborSol:Solution = nghbrFunc(actSol)
            neighborSol = jobOrderSequence(neighborSol)
            neighborSol.updateMachines()

            delta = neighborSol.objFunc() - actObj
            if delta < 0 or pow(e, -delta/temp) > random():
                actSol = neighborSol
                actObj = actSol.objFunc()

                if actObj < bestObj:
                    bestSol = actSol
                    bestObj = bestSol.objFunc()

        print(f"JobOrder SA temp:{temp:.5f} act:{actObj:.5f} | best:{bestObj:.5f}")
        temp *= alpha
    return bestSol


