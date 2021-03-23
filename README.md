# Encrypted-Dash

## Description

This programmed is designed to let you create a dash cam that encrypts the recorded video. This is not designed to be a cheap alternative to other dash cams, as you might be able to find ones with better quality for way less. This is a Proof of Concept and is meant for those who are looking for such a product with no success.

## HOW-TO:

### Manual Install:

Clone the repo

`git clone https://github.com/RaspberryProgramming/Encrypted-Dash`

Enter the repo

`cd Encrypted\ Dash`

Install pip3 and python3 (Debian based Distros)

`sudo apt install python3 python3-pip`

Install libatlas if you run into "ImportError: libcblas.so.3: cannot open shared object file..." run

`sudo apt install libatlas-base-dev`

Install Requirements

`pip3 install --upgrade -r requirements.txt`

Generate private and public keys

`python3 genkeys.py`

Create recording directory

`mkdir output`

Record video

`python3 camera.py`

Decrypt video

`python3 decryptVideo.py`

### Automated Install (Debian Based System)

Clone the repo

`git clone https://github.com/RaspberryProgramming/Encrypted-Dash`

Enter the repo

`cd Encrypted\ Dash`

Install python3

`sudo apt install python3`

Run Installer

`python3 install.py`

If you are asked to install dependencies type
`Choice [Y]:y`

If this does not show up, Run "Install Dependencies" From here, run other options as necessary.

Once finished with install.py, to run the camera type

`python3 camera.py`

Make sure that a camera is connected to the device. Next, you will need to decrypt. You can do so by typing
`python3 decryptVideo.py`


A more detailed tutorial click the link below.

**_ VIDEO TODO _**

## Parts List

- [Logitech c505e](https://www.logitech.com/en-us/products/webcams/c505e-business-webcam.960-001385.html): 55$
- [Raspberry Pi 4 1 GB](https://www.adafruit.com/product/4295) $35
- [Adafruit PiRTC PCF8523](https://www.adafruit.com/product/3386) $6
- [CR1220 Coin Battery](https://www.adafruit.com/product/380) $1
- [Samsung Micro SD 16GB](https://www.adafruit.com/product/2693) $20
- [Insignia Car Charger](https://www.bestbuy.com/site/insignia-vehicle-charger-black/6257430.p?skuId=6257430): $20

Subtotal: $137

Tax: 11.13125

Total: $148.13 (does not consider shipping)

## TODO:

- Add function/setting to rotate image
- Add how to install including RTC setup
- Add functionality to add multiple cameras
- Add Logging Functionality
- Add video tutorial
- Add improved versioning for save format
