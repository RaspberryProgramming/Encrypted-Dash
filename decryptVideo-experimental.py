import numpy as np
import cv2
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
import os
import sys
from datetime import datetime
from tqdm import tqdm
from multiprocessing import Pool, TimeoutError, cpu_count
import time

def ev2Time(filename):
    """
    filename: filename in ev format
    Removes ev format and outputs time as a float
    """
    return float(filename[:-4])

def splitRecordings(files, dist=10.0):
    """
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

def decrypt(path, private_key):
    """
    Decrypts jpg data using a given private key

    data: encrypted jpg byte data
    private_key: private key used to decrypt jpg data
    return: jpg byte data
    """
    file_in = open(path, 'rb') # Open file session

    # Retrieve session key, tag, ciphertext and nonce from file
    enc_session_key, nonce, tag, ciphertext = \
    [ file_in.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]

    file_in.close() # Close session

    # Decrypt the session key
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)

    return data

def worker(filename):
    """
    Worker function to decrypt and convert .ev to a writable format
    filename: name of the file to read in and convert
    return: None if there is an error, decrypted frame if successful
    """

    try:
        global directory
        global private_key

        data = decrypt(directory + "/" + filename, private_key) # Decrypt the file data

        nparr = np.frombuffer(data, np.int8) # Convert jpeg data to numpy array


        frame = cv2.imdecode(nparr, flags=1) # decode numpy array
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # convert frame to RGB

        return frame

    except ValueError as e: # Detects when a frame fails to decrypt
        print("\n[!] Failed to decrypt frame %s\n" % (filename))
        print(e)
        return None



directory = "output" # Directory where encrypted frames are stored

# Retrieve the private key
file_in = open("private.pem")
private_key = RSA.import_key(file_in.read())
cipher_rsa = PKCS1_OAEP.new(private_key)
file_in.close()

# Get a list of files in the directory
files = os.listdir(directory)
files.sort()

recordings = splitRecordings(files)

selected = [] # Stores list of selected recordings

while (len(selected) < 1):

    print("Recordings:\n")
    for i in range(len(recordings)):
        rname = ev2Time(recordings[i][0])) # Convert filename to time format
        rname = datatime.fromtimestamp(rname) # Convert time to timestamp
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
        selected  = range(recordings)

    else:
        try:
            for s in returnedText.split(','): # Split input by ,

                selected.append(int(s)) # append each selected recording to selected list
        except:
            print("Input not formatted correctly")
            selected = [] # Reset selection sequence



for i in selected: # For each file
    # Create video writer session
    x = recordings[i]

    # Determine the output's Filename
    rname = x[0][:-4] + ".avi"

    print(rname + " "*20) # Print the output filename

    firstfile = directory + "/" + x[0] # Path to first file

    dimensions = getDimension(decrypt(firstfile, private_key)) # Get dimension of given recording

    length = ev2Time(recording[-1]) - ev2Time(recording[0]) # Length of time for recording

    fps = len(x) / length # calculate fps

    try:
        with Pool(cpu_count()) as pool:
            results = list(tqdm(pool.imap(worker, x), total=len(x), unit="frame"))
        #pool = Pool(cpu_count(), worker_init, [private_key, pbar])
        #results = pool.map(worker, x)

    except KeyboardInterrupt:
        pool.terminate()
        pool.close()
        break
        
    
    # Create video writer session
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(rname, fourcc, fps, dimensions) # output.avi is the output file

    for r in results:
        
        if (r is not None):
            out.write(r)

    out.release()