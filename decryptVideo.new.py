import numpy as np
import cv2
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from PIL import Image
import io
import os
import sys
import sr
from multiprocessing import Process, Queue
import time

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

def worker(queue, filename):
    try:
        data = decrypt(directory + "/" + filename, private_key) # Decrypt the file data

        # Convert jpeg data to numpy array
        nparr = np.frombuffer(data, np.int8)
        frame = cv2.imdecode(nparr, flags=1) # decode numpy array
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # convert frame to RGB
        queue.put((filename, frame))

    except ValueError as e: # Detects when a frame fails to decrypt
        print("\n[!] Failed to decrypt frame %s\n" % (filename))
        print(e)
        queue.put((filename, None))
    except:
        print("\n[!] Unknown Error when decrypting and converting frame\n")
        queue.put((filename, None))

def writer(queue, filename, fps, dimensions):
    result = queue.get()
    # Create video writer session
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(filename, fourcc, fps, dimensions) # output.avi is the output file

    while (result is not None):
        if (result[1] is not None):
            out.write(result)
        print(len(result))
        result = queue.get()

    out.release()
    print("Writer Finished")
    

directory = "output" # Directory where encrypted frames are stored

procs = 8 # Default number of processes the program can run at a time

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

numOfFiles = 0

workerQueue = Queue() # Queue for decrypted frames
writerQueue = Queue() # Queue for writing frames

for x in selected:
    numOfFiles += len(recordings[x])

totstart = time.time()

for i in selected: # For each file
    # Create video writer session
    x = recordings[i]
    rname = x[0][:-4] + ".avi"
    print(rname + " "*20)

    path = directory + "/" + x[0] # Path to first file

    dimensions = getDimension(decrypt(path, private_key)) # Get dimension of given recording

    length = sr.ev2Time(x[-1]) - sr.ev2Time(x[0]) # Length of time for recording
    fps = len(x) / length # calculate fps

    # Create video writer session
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(rname, fourcc, fps, dimensions) # output.avi is the output file

    frames = []
    processes = []
    waitFrame = 0 # Frame the program is waiting to write

    for i in range(procs):
        # Create # of procs processes
        worker_proc = Process(target=worker, args=(workerQueue, x[i]))
        worker_proc.start()
    
    #for y in range(0, len(x), procs):
    frameCount = procs # Current Frame #

    recLength = len(x) # Length of the current recording
    
    writer = Process(target=writer, args=(writerQueue, rname, fps, dimensions))
    writer.start()
    while (frameCount < recLength):
        try:
    #       start = time.time() # Used to calculate fps
            
            frame = workerQueue.get()
            if frame[0] == x[waitFrame]:
                if frame[1] is not None:
                    writerQueue.put(frame[1])

                waitFrame += 1
                
                if len(frames) > 0:

                    while (len(frames) > 0 and frames[0][0] == x[waitFrame]):
                        if frames[0][1] is not None:
                            writerQueue.put(frames[0][1])
                        waitFrame += 1
                        frames.remove(frames[0])

            elif (len(frames) > 0):
                i = 0
                
                while (i < len(frames) and sr.ev2Time(frame[0]) < sr.ev2Time(frames[i][0])):
                    i += 1
                
                frames.insert(i, frame)

            else:
                frames.append(frame)

            worker_proc = Process(target=worker, args=(workerQueue, x[frameCount]))
            for i in range(len(processes)):
                if not processes[i].is_alive():
                    processes[i].join()
                    processes[i] = worker_proc
            worker_proc.start()


            #frameSort(frames) # Sort the frames that came from the queue

            #for f in frames:
            #    if f[1] is not None:
            #        out.write(f[1]) # Write the frame to the output file

            
            frameCount += 1

            #stop = time.time() # Used to calculate fps

            #fps = len(frames)/(stop-start)

            # Display current progress
#            print("Decrypted %d%% or %i/%i of frames at * fps." % ((frameCount/numOfFiles)*100, frameCount, numOfFiles), end="\r")

        except KeyboardInterrupt: # Detects when user ends the program
            print("[*] Video Decryption ended early")
            out.release() # Release the video writer

            import sys
            sys.exit(0)

    for p in processes:
        p.join()

    print("All Processes Ended")

    print("Finishing")
    print(workerQueue.full())
    while (workerQueue.full()):
        frame = workerQueue.get()
        if frame[0] == x[waitFrame]:
            if frame[1] is not None:
                writerQueue.put(frame[1])
            waitFrame += 1

            if len(frames) > 0:

                while (len(frames) > 0 and frames[0][0] == x[waitFrame]):
                    if frames[0][1] is not None:
                        out.write(frames[0][1])
                    waitFrame += 1
                    frames.remove(frames[0])

        elif (len(frames) > 0):
            i = 0

            while (sr.ev2Time(frame[0]) < sr.ev2Time(frames[i][0]) and i < frames):
                i += 1

            frames.insert(i, frame)

        else:
            frames.append(frame)
    
    writerQueue.put(None)
    writer.join()
    #out.release() # Release the video writer

totstop = time.time()

print(totstop-totstart)
print("Finished")
