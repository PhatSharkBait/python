"""
This script was written by: Cameron Bass
Email: cameronjudd98@gmail.com

This script generates user setup files that points directories at each other to help solve reference issues

MAKE SURE YOU UPDATE THE DIRECTORIES AND THE PATH YOU WANT TO SAVE YOUR FILES TO
"""
import os

#CHANGE DIRECTORIES HERE
directoriesToUse = {
    "Ben" : "c:/Users/Benjamin Hood/Perforce/BenH_DESKTOP-G8EL9O9_Just1/maya",
    "Cam" : "Z:/Work/School/JOOTD/Maya",
    "Matt" : "/Users/mattpoast/MatthewP_Matts-MacBook-Pro-3_198/Maya",
    "Chris" : "/Users/christopherslinker/Documents/JustOneOfThoseDays/Maya",
    "Carrisa" : "C:/Users/caris/Desktop/Perforce/Maya",
    "Sam" : "E:/Perforce/Sam/Maya"
}

for key in directoriesToUse.keys():
    #This is where the user setup files will be saved on your machine
    #CHANGE PATH HERE
    path = f'C:/Users/sweet/Desktop/setupFiles/{key}'
    try:
        os.mkdir(path)
        print("Folder %s created" % path)
    except FileExistsError:
        print("Folder %s already exists" % path)

    file = open(f"{path}/userSetup.py", "w")
    file.write("#Remap Directories\n")
    file.write("import maya.cmds as cmds\n")
    file.write("cmds.dirmap( en=True )\n")

    for value in directoriesToUse.values():
        if directoriesToUse[key] != value:
            file.write(f"cmds.dirmap( m= (\"{value}\", \"{directoriesToUse[key]}\"))\n")

    #If you want to add more lines to your user setup files, you can do so here