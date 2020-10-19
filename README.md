# ImageDir-to-pptx
Monitoring of image directory and importation of new experiments to powerpoint file.

Assumption:
User takes fluorescent images on Thermo scientific EVOS-FL microscope.
The microscope image filename follows the default syntax : name_filter_imagecount.tiff

Prerequisite: 
- Python version 3.6 or 3.7
- python-pptx
- watchdog

Install required packages using the following command:

'''
pip install python-pptx
pip install watchdog
'''

How to use:
1. Install required packages
2. Define directory to observe in Dir_observer.py
3. Run Dir_observer.py to start

This project is to automate the importation of user taken microscope images into powerpoint slides when new images are detected.
The script creates a pptx for every new image folder detected in the target directory.
