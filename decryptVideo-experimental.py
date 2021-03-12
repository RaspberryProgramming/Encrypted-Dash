import numpy as np
import cv2
from algorithms import AesInterface
import os
import sys
from datetime import datetime
from tqdm import tqdm
from multiprocessing import Pool, TimeoutError, cpu_count
import time
import argparse

###########################################
# Functions                               #
###########################################

def ev2Time(filename):
    """
    Convert .ev filename format to epoch time

    filename: filename in ev format
    """
    return float(filename[:-4])

def extFilter(files, extension):
    """
    Filters out any files without the selected extension
    files: list of filenames
    """
    remove = []
    for i in range(len(files)):
        try:
            fext = files[i].split(".")[-1] # File extension extracted
            if fext != extension:
                remove.append(files[i])
        except:
            remove.append(files[i])

    for r in remove:
        files.remove(r)
    
    return files

def decrypt(filename):
    """
    """
    file_in = open(filename, 'rb')
    plaintext = aes.decrypt(file_in.read())
    file_in.close()

    return plaintext


def splitRecordings(files, dist=10.0):
    """
    Splits list of .ev files and splits them based on dist into different recordings

    files: list of files using .ev format
    dist: Distance in seconds where each recording must be to split, defaulted to 10.0s
    """
    recordings = []
    recording = -1
    previous = 0.0
    
    for f in files:
        t =ev2Time(f) # Convert the filename to Time float

        if (abs(t-previous) > dist): # Check if this is a part of a new recording
            recording += 1 # Create new recording
            recordings.append([])

        recordings[recording].append(f) # Append the file to it's recording
        previous = t # Set previous to the time file we just appended

    return recordings

def getDimension(data):
   """
   Using given jpeg data getDimension will calculate the dimensions of the image.
   
   data: JPG byte data

   return: [height, width]
   """
   # open image for reading in binary mode

   # read the 2 bytes
   a = data[163:165]

   # calculate height
   height = (a[0] << 8) + a[1]

   # next 2 bytes is width
   a = data[165:167]

   # calculate width
   width = (a[0] << 8) + a[1]

   return (width, height)

def worker(filename):
    """
    Worker function to decrypt and convert .ev to a writable format for multiprocessing.Pool

    filename: name of the file to read in and convert

    return: None if there is an error, decrypted frame if successful
    """

    try:
        # Grab constant global variables
        global rec_dir

        data = decrypt(rec_dir + "/" + filename) # Decrypt the file data

        nparr = np.frombuffer(data, np.int8) # Convert jpeg data to numpy array


        frame = cv2.imdecode(nparr, flags=1) # decode numpy array
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # convert frame to RGB

        return frame

    except ValueError: # Detects when a frame fails to decrypt
        return None

    except TypeError:
        return None

def start_pool(recording, rec_dir, procs):
    """
    Starts decryption process for a recording using multiprocessing pool

    recording: list of .ev filenames for recording
    rec_dir: input directory with recording files
    procs: Number of processes to run

    return: True for success, False for failure
    """
    recordingTime = ev2Time(recording[0])

    # Determine the output's Filename
    rname = str(datetime.fromtimestamp(recordingTime)) + ".mp4"

    print(rname + " "*20) # Print the output filename

    firstfile = rec_dir + "/" + recording[0] # Path to first file

    dimensions = getDimension(decrypt(firstfile)) # Get dimension of given recording

    length = ev2Time(recording[-1]) - ev2Time(recording[0]) # Length of time for recording

    fps = len(recording) / length # calculate fps

    try:
        # Create pool of workers to decrypt recording
        pool = Pool(procs)
        # Recording is output to results
        results = pool.imap(worker, recording)
                

        # Create video writer session
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(rname, fourcc, fps, dimensions) # output.avi is the output file

        tq = tqdm(total=len(recording), unit="frame") # Create Progress bar

        # Writing each frame to video file
        for r in results:

            if (r is not None):
                out.write(r)

            tq.update() # Update Progress Bar

    except KeyboardInterrupt: # If keyboard interrupt activated, the decryption will end
        pool.terminate()
        pool.close()

        print("[*] Video Decryption ended early")

        return False

    out.release() # Release writing session
    return True

if __name__ in '__main__':

    ######################################################
    # Preparations                                       #
    ######################################################

    # Parse Arguments
    parser = argparse.ArgumentParser(description='Retrieve command arguments')

    parser.add_argument("--all", help="Decrypt all recordings and skip selection menu",
                        action="store_true")

    parser.add_argument("--procs", help="Specifies the number of processes to use",
                        type=int)

    parser.add_argument("--recdir", help="Specifies where the program will search for .ev frames",
                        type=str)

    parser.add_argument("--privkey", help="Specifies path to private key .pem file in working directory",
                        type=str)

    args = parser.parse_args()

    # Argument check

    if args.all:
        selected = True

    if args.procs:
        procs = args.procs
    else:
        procs = cpu_count()

    if args.recdir:
        rec_dir = args.recdir
    else:
        rec_dir = "output"

    if args.privkey:
        key_fn = args.privkey

    else:
        key_fn = "private.pem"

    # Load private key
    aes = AesInterface()

    if (aes.load_keys(privatefile=key_fn) == -1):
        sys.exit(1) # Exit if an error occurs

    # Get a list of files in the directory
    files = os.listdir(rec_dir)
    extFilter(files, "ev")
    files.sort()
    

    recordings = splitRecordings(files) # split list with files into individual lists for each recordings

    # Selection menu

    if 'selected' not in globals():
        selected = [] # Stores list of selected recordings

    else:
        selected = range(len(recordings)) # Skip selection menu
        
    while (len(selected) < 1): # Loop as long as there haven't been a selected recording

        print("Recordings:\n")
        for i in range(len(recordings)):
            rname = ev2Time(recordings[i][0]) # Convert filename to time format
            rname = datetime.fromtimestamp(rname) # Convert time to timestamp
            print("[%i] %s" %(i,rname))

        # Print menu
        print("Please select one or more recordings. Type A for all")
        print("or type the number of the recording you'd like to decrypt")
        print("If you'd like to decrypt multiple, type in each with a comma")
        print("between like so")
        print("'1,5,9'")
        print("Recordings:", end="")
        
        returnedText = input()

        if returnedText in ["A", "a", "All", "ALL"]: # Decrypt all recordings
            selected  = range(len(recordings))

        else:
            try:
                for s in returnedText.split(','): # Split input by ,

                    selected.append(int(s)) # append each selected recording to selected list
            except:
                print("Input not formatted correctly")
                selected = [] # Reset selection sequence

    #####################################################
    # Running the Code                                  #
    #####################################################

    for i in selected: # For each file
        
        recording = recordings[i] # Copy the current recording to a single variable
        
        if (not start_pool(recording, rec_dir, procs)): # Break loop if program failed
            break

