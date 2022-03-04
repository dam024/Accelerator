#
#  Accelerator.py
#
#
#  Created by Jaccoud Damien on 18.12.21 © Copyright
#
#  Modified by : Thomas DuBois
#
#  This program is due to run multiple simulation simultaniously, by using all CPU. The goal is to accelerate simulations by executing multiple of them at a time. 
#
#
#  Source code : https://github.com/dam024/Accelerator
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


# Function used by process to run a new simulation. When finished, send a new simulation if one is available
def launchNextProgram(index, array,display):
    # print(index.get())
    #print("Parent :",parent)
    if not index.empty():  # Tester d'utiliser des Locks, afin de bloquer l'exécution de la récupération d'index en même temps
        try:  # It happends that two process try to get exactly at the same time the get. If it's the end of the queue, it's a problem, because one process will wait untile a new element is added on the queue (it means undefinitavely). So I put a timeout, after what the get() method threw an exception. Si with this code, it's perfectly handled.
            current = index.get(timeout=0.1)  # set a timeout, so that if no element is found the program don't wait for an element... I had the bug that it was sometimes blocked at the end, so it was not
        except:
            return

        x = subprocess.run(current[0], shell=True, capture_output=True)  # Run simulation
        if x.returncode != 0:
            print("Cmd", current[0], "exit with error code :", x.returncode)
            print(x.stderr.decode("utf-8"))
        print("Done " + str(current[1] + 1) + "/" + str(len(array)))
        if display:
            print(x.stdout.decode("utf-8"))

        if index.empty():  # index.value == len(array):  # if simulations has not been runed, create a new process to run it
            pass
        else:
            p = Process(target=launchNextProgram, args=(index, array,display))
            p.start()
            p.join()
            p.close()
    else:
        pass


# Main class to handle processes
class Accelerator:
    inputFile = ''
    cmd = []
    display = False

    def __init__(self, inputFile,display):
        self.inputFile = inputFile
        self.display = display
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
        self.t = Queue()

        for i in range(len(self.cmd)):
            self.t.put([self.cmd[i], i])
        proc = []  # Les process
        for i in range(min(nb, len(self.cmd))):
            p = Process(target=launchNextProgram, args=(self.t, self.cmd,self.display))
            p.start()
            proc.append(p)
            # time.sleep(0.1)  # To desincronize simulations

        for i in range(len(proc)):
            #print("Join process",i,"\n",proc[i])
            proc[i].join()
            #print("Terminate process",i)
            proc[i].close()
            #print("Close successfull of processs",i)

        # os.wait()  # Attend que tous les process soient termines

    def launchNewProcess(self):
        #print("Prepare to launch process")
        p = Process(target=launchNextProgram, args=(self.t, self.cmd,self.display))
        p.start()
        p.join()
        #print("Terminate new Process")
        p.close()
        #print("Close successfull")


if __name__ == "__main__":
    inputFile = "cmd.txt"
    displayOut = "0"
    if len(sys.argv) > 1:
        inputFile = sys.argv[1]
    if len(sys.argv) > 2:
        displayOut = sys.argv[2]
    print("Input : ", inputFile)
    acc = Accelerator(inputFile,displayOut != "0")
