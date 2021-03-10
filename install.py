#!/usr/bin/python3
import os
import subprocess
import sys
from crontab import CronTab

print("""This script is meant to run on a debian based system.
If you are running anything else, please CTRL+C. Otherwise, press enter
to begin installation.""")

input("Ready: ")

#####################################
# function Definitions              #
#####################################

def genkeys():
    """
    Generates and writes new private and public keys using genkey.py.
    The keys will be stored in the local folder. Make sure to copy
    private.pem to a safe location and delete it from insecure storage.
    """
    import genkey
    genkey.writeNewKeys()

def input_default(prompt, default):
    """
    Input method that uses a default value

    """

    value = input("%s [%s] :" % (prompt, default))

    if (value == ""):
        value = default

    return value

def setupBoot():
    """
    Creates config to run the camera script at boot.
    """

    jobs = [i for i in cron.find_comment(comment)] # Get list of jobs

    if (len(jobs) > 0): # If there are more jobs than necessary
        print("[ ! ] More instances in boot than expected. Would you like to delete them all?")
        for j in jobs:
            print(j)
        selection = input_default("Yes or No", "Yes")

        if (selection.upper in ["Y", "YES"]):
            for j in jobs:
                j.delete()
        
    
    # Retrieve necessary data to create job

    cmdpath = input_default("Path to camera Script ", os.getcwd()+"/camera.py") 

    minfree = input_default("Sets the minimum amount of memory that the camera will leave free", "5.0")

    out = input_default("Output director for frames to be written to", os.getcwd()+"/output")

    height = input_default("Sets the height of video output", "480")

    width = input_default("Sets the width of video output", "640")
    
    public_key = input_default("Sets the default location for the public key", "public.pem")

    # Generate command

    command = "%s --minfree %s -- out %s --height %s --width %s --publickey %s" % (cmdpath, minfree, out, height, width, public_key)

    # Create job and run at boot
    job = cron.new(command=command, comment=comment)

    job.every_reboot()

    job.enable()

    if (not os.path.isdir(out)):
        os.mkdir(out)
    

def enableBoot():
    """
    """
    jobs = [i for i in cron.find_comment(comment)] # Get list of jobs
    if len(jobs) == 1:
        jobs[0].enable()
        print("[ * ] Job successfully Enabled")

    elif len(jobs) > 1:
        print("[ ! ] Too many jobs exist, please consider deleting boot and rerunning setup")
        print("[ * ] Jobs were not modified because of a conflict")

    else:
        print("[ * ] No Jobs exist")


def disableBoot():
    """
    """
    jobs = [i for i in cron.find_comment(comment)] # Get list of jobs
    if len(jobs) == 1:
        jobs[0].enable(False)
        print("[ * ] Job successfully disabled")
        
    elif len(jobs) > 1:
        print("[ ! ] Too many jobs exist, please consider deleting boot and rerunning setup")
        print("[ * ] Jobs were not modified because of a conflict")

    else:
        print("[ * ] No Jobs exist")

def deleteBoot():
    """
    """
    jobs = [i for i in cron.find_comment(comment)] # Get list of jobs
    
    for j in jobs:
        jobs[j].delete()

        print("[ * ] All Jobs have been deleted")

#####################################
# Prerequisits                      #
#####################################

# Check if pip is installed

print("[-] Installing dependencies. Please type password if prompted.")

if subprocess.call("pip3", shell=False) != 0:
    print("[-] Installing pip3")
    command = "sudo apt install python3-pip -y"
    
    output = subprocess.call(command, shell=True)

    if output != 0:
        print("[!] There was an issue when running '%s'" % (command))
        sys.exit(1)



prereq = [ # List of prerequisit commands
    "pip3 install -r requirements.txt",
]

comment = "EncryptedDash"

cron = CronTab(user=True)

for c in prereq:
    
    output = os.system(c)

    if output != 0:
        # Print error if command failed to run correctly
        print("[!] There was an issue when running '%s'" % (c))
        sys.exit(1)

#####################################
# Selection Menu                    #
#####################################

"""
selections variable stores a list of functions that can be setup using this script
Format: [name, description, function]
"""

selections = [
    ["Generate keys", "Generates private and public keys and writes them to .pem files.", genkeys],
    ["Setup Boot", "Sets up boot config", setupBoot],
    ["Enable Boot", "Enables service to run at boot", enableBoot],
    ["Disable Boot", "Disable service to run at boot", disableBoot],
    ["Delete Boot", "Deletes service to run at boot", deleteBoot],
]

selection = ""

while (selection.upper not in ["Q", "QUIT"]):
    for i in range(len(selections)):
        print("[ %d ] %s : %s" % (i, selections[i][0], selections[i][1]))
    
    selection = input("Selection: ")

    if selection.upper in ["Q", "QUIT"]:

        print("Quitting")
        pass
    
    elif int(selection) < len(selections) and int(selection) >= 0:

        selections[int(selection)][2]()

    else:
        print("[ ! ] Please pass a valid option or Q to quit")
