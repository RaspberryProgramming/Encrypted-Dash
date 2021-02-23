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
import argparse
import sys

###########################################
# Functions                               #
###########################################

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
    try:
        recipient_key = RSA.import_key(open("public.pem").read())
        session_key = get_random_bytes(16)
    except FileNotFoundError:
        print("[!] Please Generate keys with genkey.py")
        import sys
        sys.exit(0)

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
    return len(data)

######################################################
# Settings                                           #
######################################################

# Settings for any text added to frames
font                   = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (20,20)
fontScale              = 0.50
fontColor              = (255,255,255)
lineType               = 2

######################################################
# Preparations                                       #
######################################################



# Parse Arguments
parser = argparse.ArgumentParser(description='Retrieve command arguments')

parser.add_argument("--minfree", help="Sets minimum space that should be left free in Gigabytes",
                    type=float)

parser.add_argument("--out", help="Path to output folder where recordings should be written to",
                    type=float)

parser.add_argument("--height", help="Height of output video",
                    type=int)

parser.add_argument("--width", help="Width of output video",
                    type=int)

args = parser.parse_args()

# Argument check

# Minimum Free space left on harddisk in GB
if args.minfree:
    minFree = args.minfree 
else:
    minFree = 2.0

# Folder which the frames will be stored
if args.out:
    destination = args.out
else:
    destination = "./output"

if args.height and args.width:
    if (type(args.height) == int):
        dimensions = [args.height, args.width]
    else:
        print("[!] input dimensions invalid")
        sys.exit(1)

elif (args.height):
    print("[!] Argument --height requires --width argument")
    sys.exit(1)
elif (args.width):
    print("[!] Argument --width requires --height argument")
    sys.exit(1)
else:
    dimensions = [480, 640]

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

count = 0 # Keeps a count of how many frames have been recorded

#####################################################
# Running the Code                                  #
#####################################################

cap = cv2.VideoCapture(0) # Start camera capture session

cap.set(cv2.CAP_PROP_FRAME_HEIGHT, dimensions[0]) # Set max cap height
cap.set(cv2.CAP_PROP_FRAME_WIDTH, dimensions[1]) # Set max cap width


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
        total, used, free = shutil.disk_usage(destination) # Retrieve storage space stats


        if ((free // (2**30)) < minFree): # Check if there is enough space on the harddrive
            while ((free // 1073741824) < minFree): #Delete enough files to have correct storage

                fname = fr.popFirst() # Retrieve and remove the oldest frame
                os.remove(destination + "/" + fname) # Delete the oldest frame

                total, used, free = shutil.disk_usage("./") # Update storage Stats
            print(free)

        filepath = destination + "/" + str(now) + ".ev" # Generate file path to write the current frame

        # Write the frame to a file
        start = time.time()
        fsize = writeFrame(frame, filepath)
        stop = time.time()
        count += 1
        speed = (fsize/1000)/(stop-start)
        print("%d written at %d KB/s" % (count, speed), end="\r")
    else:
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
