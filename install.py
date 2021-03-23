#!/usr/bin/python3
import os
import pip
import subprocess
import sys

#####################################
# function Definitions              #
#####################################

def genkeys():
    """
    Generates and writes new private and public keys using genkey.py.
    The keys will be stored in the local folder. Make sure to copy
    private.pem to a safe location and delete it from insecure storage.
    """
    import genkey # Import genkey

    sizes = ["1024", "2048", "4096", "8192"] # List of acceptable keysizes

    print("\n\nThe following keysizes are valid:")

    for i in sizes:
        print("    %s"%i)

    keysize = input("Keysize: ") # retrieve input for keysize

    while(keysize not in sizes and keysize.upper() != "q"):

        keysize = input("Keysize: ") # Retieve more keysize input as long as valid keysize is not given

    if (keysize in sizes): # If we have a valid keysize
        genkey.writeNewKeys(int(keysize)) # Generate new keys
        print("Keys written to private.pem and public.pem")

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

    cron.write()
    

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
        j.delete()

        print("[ * ] All Jobs have been deleted")
    
    print("[ * ] Job removal finished...")

def install():
    """
    """

    # Check if pip is installed

    print("[-] Installing dependencies. Please type password if prompted.")

    apt_packages = ["python3-pip",
                    "libatlas-base-dev"] # Required on raspberry pi

    # apt installations
    if subprocess.call("apt", shell=False) != 0:
        print("[-] Installing apt dependencies")
        
        command = "sudo apt install -y " + " ".join(apt_packages)

        output = subprocess.call(command, shell=True)

        if output != 0:
            print("[!] There was an issue when running '%s'" % (command))
            sys.exit(1)

    else:
        print("[ ! ] Looks like you aren't running a debian based distro.")
        print("      The script will continue but may fail. You may want to install manually.")
        input("Press enter to continue:")
    

    if subprocess.call("pip3", shell=False) != 0:
        print("[-] Installing pip3")
        command = "sudo apt install python3-pip -y"
        
        output = subprocess.call(command, shell=True)

        if output != 0:
            print("[!] There was an issue when running '%s'" % (command))
            sys.exit(1)


    # Install packages

    failed = pip.main(["install", "--upgrade", "-r", "requirements.txt"])

    if failed != 0:
        # Print error if command failed to run correctly
        print("[!] There was an issue when installing python dependencies")
        sys.exit(1)
    

#####################################
# Prerequisits                      #
#####################################

try:
    comment = "EncryptedDash"

    from crontab import CronTab # Imported later to ensure that it was installed before loading

    cron = CronTab(user=True)

except ImportError:
    print("[!] Error, Module python-crontab is required.")
    print("Would you like to install dependencies?")
    answer = input("Choice [Y]:")

    if answer.upper() in "YES":
        install()
    else:
        print("Goodbye...")
        sys.exit(0)


#####################################
# Selection Menu                    #
#####################################

"""
selections variable stores a list of functions that can be setup using this script
Format: [name, description, function]
"""

selections = [
    ["Install Dependencies", "Installs dependencies and updates software. WARNING: Requires a reload of the script before other changes can be done.", install],
    ["Generate keys", "Generates private and public keys and writes them to .pem files.", genkeys],
    ["Setup Boot", "Sets up boot config", setupBoot],
    ["Enable Boot", "Enables service to run at boot", enableBoot],
    ["Disable Boot", "Disable service to run at boot", disableBoot],
    ["Delete Boot", "Deletes service to run at boot", deleteBoot],
]

selection = ""

while (selection.upper() not in ["Q", "QUIT"]):
    for i in range(len(selections)):
        print("[ %d ] %s : %s" % (i, selections[i][0], selections[i][1]))

    print("[ q ] Quit : Quits the install script")
    
    selection = input("Selection: ")

    if selection.upper() in ["Q", "QUIT"]:

        print("Quitting")
        pass
    
    elif int(selection) < len(selections) and int(selection) >= 0:

        selections[int(selection)][2]()

    else:
        print("[ ! ] Please pass a valid option or Q to quit")
    
    print("\n\n")
