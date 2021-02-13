import numpy as np
import cv2
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from PIL import Image
import io
import os
import sys
import sr
from multiprocessing import Pool, TimeoutError, cpu_count
import time
from tqdm import tqdm

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

def frameSort(arr):
    """
    Bubble sort to sort an array of frames that come from the queue
    """
    n = len(arr) 
  
    # Traverse through all array elements 
    for i in range(n-1): 
    # range(n) also work but outer loop will repeat one time more than needed. 
  
        # Last i elements are already in place 
        for j in range(0, n-i-1): 
  
            # traverse the array from 0 to n-i-1 
            # Swap if the element found is greater 
            # than the next element 
            if sr.ev2Time(arr[j][0]) > sr.ev2Time(arr[j+1][0]): 
                arr[j], arr[j+1] = arr[j+1], arr[j] 

def worker(filename):
    try:
        global directory
        global private_key
        
        data = decrypt(directory + "/" + filename, private_key) # Decrypt the file data

        # Convert jpeg data to numpy array
        nparr = np.frombuffer(data, np.int8)
        frame = cv2.imdecode(nparr, flags=1) # decode numpy array
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # convert frame to RGB

        return frame

    except ValueError as e: # Detects when a frame fails to decrypt
        print("\n[!] Failed to decrypt frame %s\n" % (filename))
        print(e)
        return None

def worker_init(private_key, pbar):
    worker.private_key = private_key
    worker.pbar = pbar

def writer(queue, filename, frameCount, fps, dimensions):
    
    # Create video writer session
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(filename, fourcc, fps, dimensions) # output.avi is the output file
    
    print(filename)
    print(fourcc)
    print(fps)
    print(dimensions)

    frames = []

    for i in range(frameCount):

        result = queue.get()
        if (result is not None):
            out.write(result)

    #for f in frames:
    #    out.write(f[1])

    out.release()
    print("Writer Finished")
    

directory = "output" # Directory where encrypted frames are stored

# Retrieve the private key
file_in = open("private.pem")
private_key = RSA.import_key(file_in.read())
cipher_rsa = PKCS1_OAEP.new(private_key)
file_in.close()

# Get a list of files in the directory
files = os.listdir(directory)
files.sort()

recordings = sr.splitRecordings(files)

frameCount = 0 # Used for approximating progress

selected = []

while (len(selected) < 1):

    print("Recordings:\n")
    for x in range(len(recordings)): # For each file
        rname = recordings[x][0][:-4]
        print("[%i] %s" %(x,rname))

    print("Please select one or more recordings. Type A for all")
    print("or type the number of the recording you'd like to decrypt")
    print("If you'd like to decrypt multiple, type in each with a comma")
    print("between like so")
    print("'1,5,9'")
    print("Recordings:", end="")

    returnedText = input()

    if returnedText in ["A", "a", "All", "ALL"]:
        selected  = [i for i in range(len(recordings))]
    else:
        try:
            for s in returnedText.split(','):

                selected.append(int(s))
        except:
            print("Input not formatted correctly")
            selected = []

for i in selected: # For each file
    # Create video writer session
    x = recordings[i]

    # Determine the output's Filename
    rname = x[0][:-4] + ".avi"

    print(rname + " "*20) # Print the output filename

    firstfile = directory + "/" + x[0] # Path to first file

    dimensions = getDimension(decrypt(firstfile, private_key)) # Get dimension of given recording

    length = sr.ev2Time(x[-1]) - sr.ev2Time(x[0]) # Length of time for recording

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