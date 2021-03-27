import numpy as np
import cv2
from frames import Frames
import algorithms
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
    file_data = file_in.read()
    file_in.close()

    plaintext = algorithm.decrypt(file_data)

    return plaintext


def splitRecordings(frames, dist=10.0):
    """
    Splits list of .ev files and splits them based on dist into different recordings

    files: list of files using .ev format
    dist: Distance in seconds where each recording must be to split, defaulted to 10.0s

    return: recordings, recordings_info
        recordings stores a list of recordings and the filenames of each frame
        recordings_info stores a list of recordings and their frames with more info
    """
    recordings = []
    recordings_info = []
    recording = -1
    previous = 0.0
    
    while (not frames.empty()):
        frame = frames.first
        frames.deleteFirst()

        time = frame.getTimestamp() # Convert the filename to Time float

        if (abs(time-previous) > dist): # Check if this is a part of a new recording
            recording += 1 # Create new recording
            recordings.append([])
            recordings_info.append(frame)


        recordings[recording].append(str(frame)) # Append the file to it's recording
        previous = time # Set previous to the time file we just appended

    return recordings, recordings_info

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

def worker(file_frame):
    """
    Worker function to decrypt and convert .ev to a writable format for multiprocessing.Pool

    file_frame: name of the file to read in and convert

    return: None if there is an error, decrypted frame if successful
    """

    try:
        # Grab constant global variables

        data = decrypt(rec_dir + "/" + file_frame) # Decrypt the file data

        nparr = np.frombuffer(data, np.int8) # Convert jpeg data to numpy array


        frame = cv2.imdecode(nparr, flags=1) # decode numpy array
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # convert frame to RGB

        return frame

    except ValueError: # Detects when a frame fails to decrypt
        return None

    except TypeError:
        return None

def start_pool(recording, rec_dir, procs, recording_info):
    """
    Starts decryption process for a recording using multiprocessing pool

    recording: list of .ev filenames for recording
    rec_dir: input directory with recording files
    procs: Number of processes to run

    return: True for success, False for failure
    """

    recordingTime = recording_info.getTimestamp()

    # Determine the output's Filename
    rname = str(datetime.fromtimestamp(recordingTime)) + ".mp4"

    print(rname + " "*20) # Print the output filename

    firstfile = rec_dir + "/" + recording_info.filename # Path to first file

    dimensions = getDimension(decrypt(firstfile)) # Get dimension of given recording

    length = recording_info.getTimestamp(filename=recording[-1]) - recording_info.getTimestamp() # Length of time for recording

    fps = len(recording) / length # calculate fps

    # Create video writer session
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(rname, fourcc, fps, dimensions) # output.avi is the output file

    tq = tqdm(total=len(recording), unit="frame") # Create Progress bar

    try:
        # Create pool of workers to decrypt recording
        pool = Pool(procs)
        # Recording is output to results
        results = pool.imap(worker, recording)

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
        procs = cpu_count()-1

    if args.recdir:
        rec_dir = args.recdir
    else:
        rec_dir = "output"

    if args.privkey:
        key_fn = args.privkey

    else:
        key_fn = "private.pem"

    if not os.path.isfile(key_fn):
        print("[!] Please pass a valid filename for the privkey")
        sys.exit(1)

    # Set new recursion limit
    sys.setrecursionlimit(10000)

    # Get a list of files in the directory
    frames = Frames()
    frames.importFrames(rec_dir)

    recordings, recordings_info = splitRecordings(frames) # split list with files into individual lists for each recordings

    algorithm = None # Used so the variable is accessible globally

    # Selection menu

    if 'selected' not in globals():
        selected = [] # Stores list of selected recordings

    else:
        selected = range(len(recordings)) # Skip selection menu
        
    while (len(selected) < 1): # Loop as long as there haven't been a selected recording

        print("Recordings:\n")
        for i in range(len(recordings)):
            rname = recordings_info[i].getTimestamp() # Convert filename to time format
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

        if returnedText.upper() in "ALL": # Decrypt all recordings
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
        

        # Extract algorithm key
        algorithm_key = recordings_info[i].algorithm()

        if algorithm_key not in algorithms.algorithms: # If non exists set to default
            algorithm_key = ""

        algorithm = algorithms.algorithms[algorithm_key]() # Load algorithm into algorithm variable

        # Determine key filename        

        if key_fn[-4:] != algorithm.file_extension: # If the key does not match the algorithm's file extension
            print("[*] invalid file extension for recording's encryption algorithm. Will default to private%s" % algorithm.file_extension)
            tmp_key_fn = "private%s" % algorithm.file_extension # set temporary key to private.EXT
        else:
            tmp_key_fn = key_fn # copy key_fn to tmp_key_fn

        # Load Private Key
        if (algorithm.load_keys(privatefile=tmp_key_fn) == -1): # if the keys don't exist
            print("[!] Error loading private key with extension %s" % algorithm.file_extension)
            sys.exit(1) # Exit if an error occurs

        # Generate String list of frames
        
        if (not start_pool(recording, rec_dir, procs, recordings_info[i])): # Break loop if program failed
            break

