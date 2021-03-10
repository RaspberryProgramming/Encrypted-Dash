# Encrypted-Dash

This programmed is designed to let you create a dash cam that encrypts the recorded video.

##HOW-TO:

Clone the repo

`git clone https://github.com/RaspberryProgramming/Encrypted-Dash`

Enter the repo

`cd Encrypted\ Dash`

Install Requirements

`pip3 install -r requirements.txt`

Generate private and public keys

`python3 genkeys.py`

Create recording directory

`mkdir output`

Record video

`python3 camera.py`

Decrypt video

`python3 decryptVideo.py`

If you would like to use the installer, view the video tutorial using it is below

**_ VIDEO TODO _**

# Parts List

- [Logitech c505e](https://www.logitech.com/en-us/products/webcams/c505e-business-webcam.960-001385.html)
- [Raspberry Pi 4 1 GB](https://www.adafruit.com/product/4295)
- [Adafruit PiRTC PCF8523](https://www.adafruit.com/product/3386)
- [CR1220 Coin Battery](https://www.adafruit.com/product/380)
- [Samsung Micro SD 16GB](https://www.adafruit.com/product/2693)
- [Insignia Car Charger](https://www.bestbuy.com/site/insignia-vehicle-charger-black/6257430.p?skuId=6257430)

# TODO:

- Add function/setting to rotate image
- Add how to install including RTC setup
- Add functionality to add multiple cameras
- Add Logging Functionality
- Add video tutorial
