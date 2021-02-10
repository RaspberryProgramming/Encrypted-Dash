import numpy as np
import cv2
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from PIL import Image
import io
import os
import sys
import sr

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

def decrypt(data, private_key):
    """
    Decrypts jpg data using a given private key

    data: encrypted jpg byte data
    private_key: private key used to decrypt jpg data
    return: jpg byte data
    """

    # Retrieve session key, tag, ciphertext and nonce from file
    enc_session_key, nonce, tag, ciphertext = \
    [ file_in.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]


    # Decrypt the session key
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)

    return data

directory = "output"

fps = 10.0 # Fps that the output video will be set to
#dimensions = (640, 480) # 720p resolution for the output video (1280,720)

# Retrieve the private key
private_key = RSA.import_key(open("private.pem").read())
cipher_rsa = PKCS1_OAEP.new(private_key)

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

for x in selected:
    numOfFiles += len(recordings[x])

for i in selected: # For each file
    # Create video writer session
    x = recordings[i]
    rname = x[0][:-4] + ".avi"
    print(rname + " "*20)

    file_in = open(directory + "/" + x[0], "rb") # Read the file as byte data

    dimensions = getDimension(decrypt(file_in, private_key)) # Get dimension of given recording
    print(dimensions)

    # Create video writer session
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(rname, fourcc, fps, dimensions) # output.avi is the output file

    for f in x:
        frameCount += 1
        if f.split(".")[-1] == "ev": # check if the file has the correct extension

            file_in = open(directory + "/" + f, "rb") # Read the file as byte data

            try:
                data = decrypt(file_in, private_key) # Decrypt the file data
                
                #print(getDimension(data)) # TODO: ADD INITIAL DIMENSION DETECTION

                # Convert jpeg data to numpy array
                nparr = np.frombuffer(data, np.int8)
                frame = cv2.imdecode(nparr, flags=1) # decode numpy array
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # convert frame to RGB

                out.write(frame) # Write the frame to the output file

                # Display current progress
                print("Decrypted %d%% or %i/%i of frames" % ((frameCount/numOfFiles)*100, frameCount, numOfFiles), end="\r")

            except KeyboardInterrupt: # Detects when user ends the program
                print("[*] Video Decryption ended early")
                out.release() # Release the video writer

                import sys
                sys.exit(0)

            except ValueError as e: # Detects when a frame fails to decrypt
                print("\n[!] Failed to decrypt frame %s\n" % (f))

    out.release() # Release the video writer
