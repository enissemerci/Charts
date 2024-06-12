from datetime import datetime, timedelta
import pandas
from copy import deepcopy

"""
ZAMAN BİRİMLERİ DAKİKA
"""

setups = {}
machinability = {}
"""
 . . .  : : : setups : : : . . 
{
    machineName : setupTime matrix by job index
    "415"       : [[0, 2, 4, 1],
                   [2, 0, 6, 7],
                   [4, 6, 0, 8],
                   [1, 7, 8, 0]]
      .                 .
      .                 .
      .                 .
}

"""

class Job:
    def __init__(self, jobIndex:int ,jobRow:pandas.DataFrame, startDate:datetime) -> None:
        self.jobIndex = jobIndex
        self.jobRowDF = jobRow
        self.jobCode = jobRow["Malzeme kısa metni"]
        sepCode = self.jobCode.split("-")

        #setups
        self.diameter = sepCode[0].split("X")[0]
        self.length = sepCode[0].split("X")[-1]
        self.standart = sepCode[1]
        self.quality = sepCode[2]

        self.runTime = jobRow["Toplam Süre (dk)"]
        self.assignedMachineName = str(jobRow["Makine"])
        #self.dueDate = datetime.strptime(jobRow["Sevk Tarihi"], "%m/%d/%Y")  # FOR TEST-SRC.PY  
        self.dueDate = jobRow["Sevk Tarihi"] + timedelta(days=1)

        self.startDate = startDate
        self.endDate = self.startDate + timedelta(minutes=self.runTime)
    
    def getTotalTime(self) -> float:
        return (self.endDate - self.startDate).total_seconds() / 60


class Machine:
    def __init__(self, machineName:str, jobSequence:list[Job], startDate:datetime) -> None:
        self.machineName = str(machineName)
        self.jobSequence = deepcopy(jobSequence)
        self.startDate = startDate
        #self.updateJobs()

    def getSetupTime(self, job1:Job, job2:Job) -> float:
        return setups[self.machineName][job1.jobIndex][job2.jobIndex]
    
    def getJobRuntime(self, job:Job) -> float:
        return job.runTime / machinability[job.assignedMachineName]["speed"] * machinability[self.machineName]["speed"]

    def updateJobs(self):
        if not self.jobSequence: return
        lastDate = self.startDate

        for i in range(len(self.jobSequence) - 1):
            job = self.jobSequence[i]
            job.startDate = lastDate
            lastDate += timedelta(minutes=job.runTime/machinability[job.assignedMachineName]["speed"]*machinability[self.machineName]["speed"])
            #print(machinability[job.assignedMachineName]["speed"],machinability[self.machineName]["speed"])
            job.endDate = lastDate
            lastDate += timedelta(minutes=self.getSetupTime(job, self.jobSequence[i + 1]))
            #job.assignedMachineName = self.machineName

        if self.jobSequence:
            lastJob = self.jobSequence[-1]
            lastJob.startDate = lastDate
            lastJob.endDate = lastDate + timedelta(minutes=lastJob.runTime/machinability[lastJob.assignedMachineName]["speed"]*machinability[self.machineName]["speed"])
            #lastJob.assignedMachineName = self.machineName

    #TESTED
    def getCmax(self):
        try:
            return (self.jobSequence[-1].endDate - self.jobSequence[0].startDate).total_seconds() /60 / machinability[self.machineName]["capacity"]
        except IndexError:
            if len(self.jobSequence) == 0: return 0
            raise ValueError
    
    #TESTED
    def getCmaxReal(self):
        return self.getCmax() * machinability[self.machineName]["capacity"]
    
    #
    def getTardiness(self):
        total = 0
        for job in self.jobSequence:
            total += max(0, (job.endDate - job.dueDate).total_seconds()/60)
            #print(job.jobCode[:20], job.assignedMachineName, "\t", job.endDate, job.dueDate, (job.endDate - job.dueDate))
        return total
    
    def machinability(self, job:Job) -> bool:
        machineCons = machinability[self.machineName]
        if machineCons["length"][0] > float(job.length) or float(job.length) > machineCons["length"][1]: 
            #print("this length is not machinable for ", self.machineName)
            return False
        if job.diameter not in machineCons["diameter"]:
            #print("this diameter is not machinable for ", self.machineName)
            return False
        return True
    
    def machineInfo(self, jobIndexed:bool=False ,jobCodeLen:int=20):
        print(self.machineName, "\tCmax:", self.getCmaxReal(), "\tTardy:", self.getTardiness())
        print(f"{"Index" if jobIndexed else "\t"}  JobCode{" "*(jobCodeLen)}RunTime\t Tardy\t\t SetupTime")
        for job,job2 in zip(self.jobSequence[:-1], self.jobSequence[1:]):
            print(job.jobIndex, job.jobRowDF["iş indeksi"] if jobIndexed else "", " ", job.jobCode[:jobCodeLen], "\t", f"{job.runTime:.5f}" , "\t", f"{max((job.endDate - job.dueDate).total_seconds()/60,0):.5f}", "\t", self.getSetupTime(job, job2))
        lastJob = self.jobSequence[-1]
        print(lastJob.jobIndex, lastJob.jobRowDF["iş indeksi"] if jobIndexed else ""," ", lastJob.jobCode[:jobCodeLen], "\t", f"{lastJob.runTime:.5f}" , "\t",f"{max((lastJob.endDate - lastJob.dueDate).total_seconds()/60,0):.5f}")

from statistics import stdev

class Solution:
    def __init__(self, machines:list[Machine]) -> None:
        self.machines:list[Machine] = machines

    def getCmax(self) -> float:
        return max([machine.getCmax() for machine in self.machines])

    def getCmaxReal(self) -> float:
        return max([machine.getCmaxReal() for machine in self.machines])

    def getTardiness(self) -> float:
        return sum([machine.getTardiness() for machine in self.machines])

    def objFunc(self, tardy:float=0.9, cmax:float=0.09, ci_sum:float=0.01 ,cmax_sum:float=0.01, stdev_scale:float=0.0) -> float:
        return cmax*self.getCmax() + tardy*self.getTardiness() + ci_sum*sum([sum([job.getTotalTime() for job in machine.jobSequence]) for machine in self.machines]) # cmax_sum * sum([machine.getCmax() for machine in self.machines])

    #def objFunc4Output(self, tardy:float=0.9, cmax:float=0.1, cmax_sum:float=0.0, stdev_scale:float=0.0) -> float:
    #    return cmax*self.getCmax() + tardy*self.getTardiness()

    def updateMachines(self):
        for machine in self.machines: machine.updateJobs()

    def solutionInfo(self):
        print("\n . . . : : : SOLUTION INFO : : : . . . ")
        print(f"Objective Func =  {self.objFunc()}")
        print(f"Tardiness: {self.getTardiness():.5f}\tCmax: {self.getCmaxReal():.5f}")

        print("\nMACHINE\t   Tardiness\t  Cmax ")
        for machine in self.machines:
            print(f"{machine.machineName}\t = {machine.getTardiness():.5f} \t| {machine.getCmaxReal():.5f}")

    def solutionInfoDetailed(self, jobIndexed:bool=False): 
        print("\n . . . : : : SOLUTION INFO DETAILED : : : . . . ")
        print(f"Objective Func =  {self.objFunc()}")
        print(f"Tardiness: {self.getTardiness():.5f}\tCmax: {self.getCmaxReal():.5f}")
        for machine in self.machines: 
            machine.machineInfo(jobIndexed)
