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
   # open image for reading in binary mode

   # read the 2 bytes
   a = data[163:165]

   # calculate height
   height = (a[0] << 8) + a[1]

   # next 2 bytes is width
   a = data[165:167]

   # calculate width
   width = (a[0] << 8) + a[1]

   return [height, width]

directory = "output"

fps = 10.0 # Fps that the output video will be set to
dimensions = (640, 480) # 720p resolution for the output video (1280,720)

# Get a list of files in the directory
files = os.listdir(directory)
files.sort()

recordings = sr.splitRecordings(files)

numOfFiles = len(files) # Helps estimate how far along the program is at decrypting the video

# Retrieve the private key
private_key = RSA.import_key(open("private.pem").read())
cipher_rsa = PKCS1_OAEP.new(private_key)

frameCount = 0 # Used for approximating progress

for x in recordings: # For each file
    # Create video writer session
    rname = x[0][:-4] + ".avi"
    print(rname + " "*20)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(rname, fourcc, fps, dimensions) # output.avi is the output file

    for f in x:
        frameCount += 1
        if f.split(".")[-1] == "ev": # check if the file has the correct extension

            file_in = open(directory + "/" + f, "rb") # Read the file as byte data

            # Retrieve session key, tag, ciphertext and nonce from file
            enc_session_key, nonce, tag, ciphertext = \
            [ file_in.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]

            try:
                # Decrypt the session key
                session_key = cipher_rsa.decrypt(enc_session_key)

                # Decrypt the data with the AES session key
                cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
                data = cipher_aes.decrypt_and_verify(ciphertext, tag)
                
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
