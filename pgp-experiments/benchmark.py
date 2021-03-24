import aes_funct
import pgp_funct
import cv2
from PIL import Image
import io

import random

import time

if __name__ in '__main__':
    aes = aes_funct.AesInterface()
    aes.load_keys(privatefile="private.pem", publicfile="public.pem")
    pgp = pgp_funct.PgpInterface()
    pgp.load_keys(privatefile="privatekey.asc", publicfile="publickey.asc")

    
    #original = ''.join([str(random.randint(0, 9)) for i in range(10000000)]).encode()
    dimensions = [480, 640]
    cap = cv2.VideoCapture(0) # Start camera capture session

    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, dimensions[0]) # Set max cap height
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, dimensions[1]) # Set max cap width

    ret, frame = cap.read()

    img = Image.fromarray(frame, "RGB") # Convert image in numpy format to image data
    data = io.BytesIO()
    img.save(data, format='JPEG') # Convert image data to jpeg
    original = data.getvalue() # get image byte data

    start = time.time()
    ciphertext = aes.encrypt(original)
    stop = time.time()
    print("AES Encrypt: %s" % (str(stop-start)))

    start = time.time()
    plaintext = aes.decrypt(ciphertext)
    stop = time.time()
    print("AES Decrypt: %s" % (str(stop-start)))
   

    ciphertext = pgp.encrypt(original)
    plaintext = pgp.decrypt(ciphertext)

    start = time.time()
    ciphertext = pgp.encrypt(original)
    stop = time.time()
    print("PGP Encrypt: %s" % (str(stop-start)))

    start = time.time()
    plaintext = pgp.decrypt(ciphertext)
    stop = time.time()
    print("PGP Decrypt: %s" % (str(stop-start)))
    
