# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 14:07:43 2025

@author: joaquinmtorres

determining frequency of dropped frames (missing labels) and impossible jumps 
(misplaced labels) from .h5 files produced by DLC
"""
#import modules
import glob
import pandas as pd
import math

#determine location of files
fileLoc = "/Users/PCVR_103C/Desktop/Joaquin Thesis/firstStep/results/"
fileList = sorted(glob.glob(fileLoc + "*.h5")) #sorts all videos
saveLoc = "/Users/PCVR_103C/Desktop/Joaquin Thesis/firstStep/"

# Set threshold - this is the pcutoff value
threshold = 0.25

# Set empty vectors where info will be saved
file = []
drops = []
jumps = []

# Start for loop
for i in fileList:
    df = pd.read_hdf(i) #read h5 file and store as a dataframe
    
    # Take file name
    fileName = i.split("/")[-1].split("\\")[-1].split(".")[0]
    gs_pos = fileName.find("gs")
    fileName = fileName[:gs_pos + 2]
       
    # Set/Reset counters for frequency of dropped frames/impossible jumps
    dropCount = 0
    jumpCount = 0
    
    # read every row
    for index, row in df.iterrows():
        
        # Dropped frames - consider frames whose ROIs' likelihood is less than threshold
        # ROIs include snout (bodypart1) and port/hopper (objectA) - subject to change
        if row.iloc[2] < threshold or row.iloc[11] < threshold:
            dropCount += 1 #add 1 to drops counter
        
        # Impossible jumps - distance between ROIs should be less than 170px (arbitrary)
        # ROIs include snout (bodypart1) and torso (bodypart2)
        coord1 = (row.iloc[0], row.iloc[1]) #this gives coords for snout
        coord2 = (row.iloc[3], row.iloc[4]) #this gives coords for torso
        distance = math.dist(coord1, coord2) #calculate distance between coordinates
        
        if distance > 170.0:
            jumpCount += 1 #add 1 to jumps counter
    
    # Get ratios
    dropRate = dropCount/len(df)
    jumpRate = jumpCount/len(df)
    
    # Store info in vectors
    file.append(fileName) #save file name
    drops.append(dropRate) #save drop count
    jumps.append(jumpRate) #save jump count
    
# Store data into a dataframe and save as csv
saveData = pd.DataFrame({"fileName":file, "dropRate":drops, "jumpRate":jumps})
saveData.to_csv(saveLoc + "mislabels.csv", index=False)
    