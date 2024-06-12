from src import Job
import src
from datetime import datetime

"""uzunluk kısıtları??? /10 ve *10 uygulandı"""
"""
KAPASİTE VERİLERİ DEVRE DIŞI ŞU AN
"""




machinability = {
    "415"   : {"length":[0.16,1250], "diameter":["M8", "M10","M12"                     ], "capacity": 1, "speed": 150},
    "416"   : {"length":[0.20,1400], "diameter":["M12","M14","M16", "1/2\"", "5/8\""   ], "capacity": 1, "speed": 140},
    "518"   : {"length":[0.25,1600], "diameter":["M12","M14","M16", "1/2\"", "5/8\""   ], "capacity": 1, "speed": 130},
    "524"   : {"length":[0.28,2050], "diameter":["M16","M22","M24", "7/8\""            ], "capacity": 1, "speed": 130},
    "BV6"   : {"length":[0.35,2050], "diameter":["M16","M18","M20","M22","M24"         ], "capacity": 1, "speed": 85 },
    "SP58"  : {"length":[0.45,2000], "diameter":["M20"                                 ], "capacity": 1, "speed": 130},
    "SP660" : {"length":[0.48,2050], "diameter":["M20","M24","M27","M30"               ], "capacity": 1, "speed": 60 },
}

setup = {
    "415"   : {"diameter": 240, "standart":  75, "length": 15, "quality": 30}, 
    "416"   : {"diameter": 240, "standart":  75, "length": 15, "quality": 30},
    "518"   : {"diameter": 240, "standart":  75, "length": 15, "quality": 30},
    "524"   : {"diameter": 300, "standart":  90, "length": 20, "quality": 35},
    "BV6"   : {"diameter": 300, "standart":  90, "length": 20, "quality": 35},
    "SP58"  : {"diameter": 240, "standart":  75, "length": 15, "quality": 30},
    "SP660" : {"diameter": 360, "standart": 120, "length": 40, "quality": 45},
}


# Grup standartlarına göre ayırma işlevi
def groupStandart(item1:str, item2:str) -> bool:
    group1 = ["933", "931"]
    group2 = ["7990", "4017", "4014"]
    if any([g1 in item1 for g1 in group1]):
        return any([g1 in item2 for g1 in group1])
    elif any([g2 in item1 for g2 in group2]):
        return any([g2 in item2 for g2 in group2])
    else:
        return False
    
# Grup kalitesine göre ayırma işlevi
def groupQuality(item1, item2):
    group = ["5.6", "5.8", "6.8", "4.6"]
    return item1 == item2 or (item1 in group and item2 in group)

#TESTED
def calcSetup(machineSetupData:dict, job1:Job, job2:Job):
    total = 0
    if job1.diameter != job2.diameter:
        total += machineSetupData["diameter"]
        
    if job1.length != job2.length:
        total += machineSetupData["length"]
        
    if job1.standart != job2.standart and not groupStandart(job1.standart, job2.standart):
        total += machineSetupData["standart"]
        
    if job1.quality != job2.quality and not groupQuality(job1.quality, job2.quality):
        total += machineSetupData["quality"]
    
    return total

"""

#returns true if item1 and item2 requires setup time
def groupStandart(item1:str, item2:str) -> bool:
    group1 = ["933", "931"]
    group2 = ["7990", "4017", "4014"]
    if any([g1 in item1 for g1 in group1]):
        return not any([g1 in item2 for g1 in group1])
    elif any([g2 in item1 for g2 in group2]):
        return not any([g2 in item2 for g2 in group2])
    else:
        return not item1 == item2

#returns true if item1 and item2 requires setup time
def groupQuality(item1:str, item2:str) -> bool:
    if item1 == item2: return False
    group = ["5.6", "5.8", "6.8", "4.6"]
    return not (item1 in group and item2 in group) 



def calcSetup(machineSetupData:dict, job1:Job, job2:Job):
    
    total = 0
    if job1.diameter != job2.diameter:
        total += machineSetupData["diameter"]
        
    if job1.length != job2.length:
        total += machineSetupData["length"]
        
    if groupStandart(job1.standart, job2.standart):
        total += machineSetupData["standart"]
        
    if groupQuality(job1.quality, job2.quality):
        total += machineSetupData["quality"]
    
    return total

"""
#TESTED
def loadData(data, startDate:datetime):
    
    src.machinability = machinability

    jobs:list[Job] = [Job(index, 
                          data.iloc[index], 
                          startDate) 
                      for index in range(len(data))]

    for machineName in setup.keys():
        src.setups[machineName] = []
        for jobColumn in jobs:
            setupRow = []
            for jobRow in jobs:
                setupRow.append(
                    calcSetup(setup[machineName], 
                              jobColumn, 
                              jobRow))
                
            src.setups[machineName].append(setupRow)
    
    
    """
    
    for machineName in src.setups.keys():
        with open(f"setup_{machineName}.txt","w") as file:
                for row in src.setups[machineName]:
                    for column in row:
                        file.write(str(column) + ", ")
                    file.write("\n")
            
            
"""



if __name__=="__main__":
    loadData()
