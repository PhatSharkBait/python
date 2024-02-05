#This script generates usersetup files that points directories at each other to solve reference issues
#in the Just One Of Those Days project
import os

directoriesToUse = {
    "Ben" : "c:/Users/Benjamin Hood/Perforce/BenH_DESKTOP-G8EL9O9_Just1/maya",
    "Cam" : "Z:/Work/School/JOOTD/Maya",
    "Matt" : "/Users/mattpoast/MatthewP_Matts-MacBook-Pro-3_198/Maya",
    "Chris" : "/Users/christopherslinker/Documents/JustOneOfThoseDays/Maya",
    "Carrisa" : "C:/Users/caris/Desktop/Perforce/Maya",
    "Sam" : "E:/Perforce/Sam/Maya",
}

for key in directoriesToUse.keys():
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

