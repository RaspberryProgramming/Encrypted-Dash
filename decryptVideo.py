import numpy as np
import cv2
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from PIL import Image
import io
import os
import sys

directory = "output"

fps = 10.0 # Fps that the output video will be set to
dimensions = (1280, 720) # 720p resolution for the output video

# Create video writer session
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, fps, dimensions) # output.avi is the output file

# Get a list of files in the directory
files = os.listdir(directory)
files.sort()

numOfFiles = len(files) # Helps estimate how far along the program is at decrypting the video

# Retrieve the private key
private_key = RSA.import_key(open("private.pem").read())
cipher_rsa = PKCS1_OAEP.new(private_key)

for i in range(numOfFiles): # For each file
    f = files[i]
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

            # Convert jpeg data to numpy array
            nparr = np.frombuffer(data, np.int8)
            frame = cv2.imdecode(nparr, flags=1) # decode numpy array
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # convert frame to RGB
            out.write(frame) # Write the frame to the output file

            # Display current progress
            print("Decrypted %d%% or %i/%i of frames" % ((i/numOfFiles)*100, i, numOfFiles), end="\r")

        except KeyboardInterrupt: # Detects when user ends the program
            print("[*] Video Decryption ended early")
            out.release() # Release the video writer

            import sys
            sys.exit(0)

        except ValueError as e: # Detects when a frame fails to decrypt
            print("\n[!] Failed to decrypt frame %s\n" % (i))
        
        


out.release() # Release the video writer
