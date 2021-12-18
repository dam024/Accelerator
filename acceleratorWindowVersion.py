#
#  Accelerator.py
#
#
#  Created by Jaccoud Damien on 18.12.21, I was drunk when I coded this
#  Window version
#
#  Modified by : 
#
#  This program is due to run multiple simulation simultaniously, by using all CPU. 
#
#
#
#
#
#  Usage : python3 accelerator.py <cmdFile>
#  <cmdFile> : txt file containing all commands to run simulations. Ex : ./program agruments  -> one and only one cmd per line
#
#
#

import sys
import os
from multiprocessing import Process, cpu_count, Queue, Value, Array
import subprocess
import time


#Function used by process to run a new simulation. When finished, send a new simulation if one is available
def launchNextProgram(index, array, acc, i):
    if index.value < len(array):
        j = index.value
        index.value += 1
        current = array[j]
        x = "test"
        os.system(current) #subprocess don't work on window need to check
        #x = subprocess.run([current], shell=True, capture_output=True)# Run simulation
        print("Done " + str(j + 1) + "/" + str(len(array)))
        if index.value == len(array):# if simulations has not been runed, create a new process to run it
            pass
        else:
            p = Process(target=launchNextProgram, args=(index, array, acc, i))
            p.start()
            p.join()
            p.close()


#Main class to handle processes
class Accelerator:
    inputFile = ''
    cmd = Queue()
    test = 0

    def __init__(self, inputFile):
        self.inputFile = inputFile
        print(self.inputFile)
        if os.path.isfile(self.inputFile):
            with open(self.inputFile) as my_file:
                self.cmd = my_file.readlines()
                # for i in range(1, 10):
                #    print(self.cmd[i])
                self.execute()

    def __iter__(self):
        return self

    def __next__(self):
        return self

    def execute(self):
        nb = cpu_count()
        print(nb, len(self.cmd))
        self.t = Value('i', 0)
        proc = []  # Les process
        for i in range(nb):
            p = Process(target=launchNextProgram, args=(self.t, self.cmd, self, i))
            p.start()
            proc.append(p)
            time.sleep(0.1)#To desincronize simulations

        for i in range(len(proc)):
            proc[i].join()
            proc[i].close()

        # os.wait()  # Attend que tous les process soient termines

    def launchNewProcess(self):
        print("Prepare to launch process")
        p = Process(target=launchNextProgram, args=(self.t, self.cmd, self, -1))
        p.start()
        os.wait()


if __name__ == "__main__":
    inputFile = "test.txt"
    if len(sys.argv) > 1:
        inputFile = sys.argv[1]
    print("Input : ", inputFile)
    acc = Accelerator(inputFile)
