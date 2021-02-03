import numpy as np
import cv2
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from PIL import Image
import io
import time
from datetime import datetime
import frames
import shutil
import os

def writeFrame(frame, filepath):
    """
    Encrypts and writes the frame to a file. The function uses
    frame: numpy image frame data
    filepath: path, including file to save the data
    """
    
    img = Image.fromarray(frame, "RGB") # Convert image in numpy format to image data 
    data = io.BytesIO()
    img.save(data, format='JPEG') # Convert image data to jpeg
    data = data.getvalue() # get image byte data
    
    # Load the private key
    recipient_key = RSA.import_key(open("public.pem").read())
    session_key = get_random_bytes(16)

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)
    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data)

    # Write the encrypted file
    file_out = open(filepath, "wb") # Open the file session, using wb to write byte data
    [ file_out.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext) ]
    file_out.close() # Close the write session and save to disk

destination = "output" # Folder which the frames will be stored


dimensions = (1280, 720) # 720p resolution for recording video
minFree = 10.0 # Minimum Free space left on harddisk in GB
font                   = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (20,20)
fontScale              = 0.30
fontColor              = (255,255,255)
lineType               = 2


# Check if the output destination exists
if not (os.path.exists(destination)):
    print("[!] Error: '%s' path does not exist" % (destination))
    import sys
    sys.exit(0)

files = os.listdir(destination) # Get list of files in destination path
files.sort() # Sort the files in order from oldest to newest frame

fr = frames.Frames() # Frames class object is used to store a queue of frames

for f in files: # Put each file into the Frames object
    fr.append(f)

cap = cv2.VideoCapture(0) # Start camera capture session

while(True):
    # Capture new frame
    ret, frame = cap.read()

    if ret==True: # If frame retrieval was successful

        # Timestamp the Frame
        now = time.time() # Retrieve the current time

        # Create a human readable timestamp
        timestamp = datetime.fromtimestamp(now).strftime("%m/%d/%Y %H:%M:%S.%f")

        # Stamp the timestamp onto the current frame
        cv2.putText(frame, timestamp,bottomLeftCornerOfText, 
            font, 
            fontScale,
            fontColor,
            lineType)

        # Check whether there is enough space on the disk
        total, used, free = shutil.disk_usage("./") # Retrieve storage space stats


        if ((free // (2**30)) < minFree): # Check if there is enough space on the harddrive
            fname = fr.getFirst() # Retrieve the oldest frame
            os.remove("output/" + fname) # Delete the oldest frame
            fr.deleteFirst() # Remove oldest frame from the Frames Object

        
        filepath = destination + "/" + str(now) + ".ev" # Generate file path to write the current frame

        # Write the frame to a file
        writeFrame(frame, filepath)

    else:
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
