import numpy as np
import cv2
from algorithms import AesInterface
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

    ciphertext = aes.encrypt(data)

    # Write the encrypted file
    file_out = open(filepath, "wb") # Open the file session, using wb to write byte data
    file_out.write(ciphertext)
    file_out.close() # Close the write session and save to disk
    return len(data)

if __name__ in '__main__':
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
                        type=str)

    parser.add_argument("--height", help="Height of output video",
                        type=int)

    parser.add_argument("--width", help="Width of output video",
                        type=int)

    parser.add_argument("--publickey", help="Path to public key file",
                        type=str)

    args = parser.parse_args()

    # Argument check

    # Minimum Free space left on harddisk in GB
    if args.minfree:
        minFree = args.minfree 
    else:
        minFree = 5.0

    # Folder which the frames will be stored
    if args.out:
        destination = args.out
    else:
        destination = "./output"

    # Resolution of output video
    if args.height and args.width:
        # create dimensions variable using passed dimensions
        dimensions = [args.height, args.width]

    # Display error message if one of the dimensions isn't specified while the other is
    elif (args.height):
        print("[!] Argument --height requires --width argument")
        sys.exit(1)
    elif (args.width):
        print("[!] Argument --width requires --height argument")
        sys.exit(1)

    else: # Default dimensions
        dimensions = [480, 640]

    if args.publickey: # Load public key given by arguments
        public_key = args.publickey

    else: # Default path to public key is public.pem
        public_key = "public.pem"



    aes = AesInterface() # Create interface to encrypt data
    if (aes.load_keys(publicfile=public_key) == -1):
            sys.exit(1) # exit if an error occurs

    # Check if there is enough storage to support minFree configuration
    total, used, free = shutil.disk_usage("/mnt") # Retrieve storage space stats
    if total//(2**30) <= minFree:
        print("[!] Not enough storage to support your configuration. Consider upgrading storage size or changing --minFree setting")
        sys.exit(0)

    # Check if the output destination exists
    if not (os.path.exists(destination)):
        print("[!] Error: '%s' path does not exist" % (destination))
        sys.exit(0)

    fr = frames.Frames() # Generates frame object with all frames from selected output
    fr.importFrames(destination) # Imports list of frames from folder

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


            if ((free // (2**30)) <= minFree): # Check if there is enough space on the harddrive
                while ((free // (2**30)) <= minFree): #Delete enough files to have correct storage

                    fname = fr.popFirst() # Retrieve and remove the oldest frame
                    os.remove(destination + "/" + fname) # Delete the oldest frame

                    total, used, free = shutil.disk_usage(destination) # Update storage Stats
                    print(str(free) + " "*20)

            filepath = destination + "/" + str(now) + ".ev" # Generate file path to write the current frame

            fr.append(str(now) + ".ev")# Add frame to Frames object

            # Write the frame to a file
            start = time.time()
            fsize = writeFrame(frame, filepath)
            stop = time.time()
            count += 1
            speed = (fsize/1000)/(stop-start)
            print("%d written at %d KB/s" % (count, speed), end="\r", flush=True)
        else:
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
