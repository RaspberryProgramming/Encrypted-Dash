#!/usr/bin/python3
import os
import subprocess
import sys

print("""This script is meant to run on a debian based system.
If you are running anything else, please CTRL+C. Otherwise, press enter
to begin installation.""")

input("Ready: ")

#####################################
# function Definitions              #
#####################################

def rpireq():
    """
    Installs raspberry pi os requirements in addition to any other prerequisits.
    """
    
    return subprocess.call("sudo apt install python3-picamera", shell=True)

def genkeys():
    """
    Generates and writes new private and public keys using genkey.py.
    The keys will be stored in the local folder. Make sure to copy
    private.pem to a safe location and delete it from insecure storage.
    """
    import genkey
    genkey.writeNewKeys()

def startboot():
    """
    Sets the camera script to run at boot.
    """
    print("[?] This will be implemented in future update")

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

for c in prereq:
    
    output = subprocess.call("pip3 install -r requirements.txt", shell=False)

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
    ["Raspberry Pi Requirements", "If you are running raspberry pi os, this will install any requirements even if youre running the lite version", rpireq],
]

