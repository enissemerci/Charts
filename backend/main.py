import pandas
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from copy import deepcopy
from src import Job, Machine, Solution
import publicFuncs
import metaheuristics
import reqs

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

jobs = []

def load_jobs_and_initialize(start_date):
    global jobs
    data = pandas.read_excel("Üretim Planı 14-21.09.XLSX", "Soğuk Dövme")
    reqs.loadData(data=data, startDate=start_date)
    jobs = [Job(index, data.iloc[index], start_date) for index in range(len(data))]
    return jobs

def optimize_solution(initial_solution):
    solution = deepcopy(initial_solution)
    bestSol, bestObj = solution, solution.objFunc()
    for _ in range(100):
        newSol = publicFuncs.generateRandomSolution(jobs=jobs, startDate=solution.machines[0].startDate)
        if newSol.objFunc() < bestObj:
            bestSol, bestObj = newSol, newSol.objFunc()
    
    for _ in range(20):
        solution = metaheuristics.simulatedAnnealing(bestSol, alpha=0.5, tStart=100, tEnd=1, markov=20, nghbrFunc=publicFuncs.generateNeighbor)
        if solution.objFunc() < bestObj:
            bestSol, bestObj = solution, solution.objFunc()

    return bestSol

def anneal():
    start_date = datetime.strptime("14/09/2023", "%d/%m/%Y")
    load_jobs_and_initialize(start_date)
    start_solution = publicFuncs.generateRandomSolution(jobs=jobs, startDate=start_date)
    final_solution = optimize_solution(start_solution)

    publicFuncs.solutionInfo(final_solution)
    final_solution.updateMachines()

    job_list = []
    for machine in final_solution.machines:
        job_list.extend(machine.jobSequence)

    concatenated_df = pandas.concat([job.jobRowDF for job in job_list], axis=1, ignore_index=True).T
    return final_solution

def solution2json(solution, timeUpscale=5.0):
    data = {}
    for machine in solution.machines:
        data_row = []
        for job in machine.jobSequence:
            data_row.append((f"{job.diameter}X{job.length}-{job.standart}-{job.quality}", job.runTime * timeUpscale, 20, job.jobIndex))
        data[machine.machineName] = data_row
        data[machine.machineName + "StartDate"] = machine.startDate.strftime("%a, %d %b %Y %H:%M:%S GMT")
    return data

def json2solution(solutionDict):
    machines = []
    for machineName in list(solutionDict.keys())[0::2]:
        machine = Machine(machineName, [], startDate=datetime.strptime(solutionDict[machineName + "StartDate"], "%a, %d %b %Y %H:%M:%S GMT"))
        for job in solutionDict[machineName]:
            machine.jobSequence.append(deepcopy(jobs[job[3]]))
        machines.append(machine)
    sol = Solution(machines=machines)
    sol.updateMachines()
    return sol

@app.route('/data')
def get_data():
    print("OK let get it started")
    data = solution2json(anneal(), 0.2)
    return jsonify(data)

@app.route('/custom', methods=['POST'])
def receive_custom_data():
    data = request.get_json()
    custom_data = data['customData']
    response_data = json2solution(custom_data)
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
