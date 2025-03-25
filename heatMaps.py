# -*- coding: utf-8 -*-
"""
Created on Fri Mar 21 14:56:06 2025

@author: joaquinmtorres

This code analyzes each h5 file and creates heat maps according to the coordinates
of the midpoint of the leftear and rightear (more representative). This will 
plot individual mouse data, group data (according to reinforced lever location), 
and all data.
"""

# import modules
import pandas as pd
import matplotlib.pyplot as plt
import glob
import math

# determine location of h5 files and where results would be saved
fileLoc = "C:/Users/PCVR_103C/Desktop/Joaquin Thesis/trimmedDay4/"
fileList = sorted(glob.glob(fileLoc + "*.h5")) #sorts all h5 files
saveLoc = "C:/Users/PCVR_103C/Desktop/Joaquin Thesis/trimmedDay4/results/"
# reinforced lever data
leverData = pd.read_csv("C:/Users/PCVR_103C/Desktop/Joaquin Thesis/Code/reinforcedLever.csv")


# set empty arrays for group xy coordinates (according to reinforced lever)
xLeft = []
yLeft = []
xRight = []
yRight = []


# start for loop for individual mouse heat maps
for i in range(len(fileList)):
    df = pd.read_hdf(fileList[i]) #store data as dataframe
    saveName = fileList[i].split("/")[-1].split("\\")[-1][:-52] #saves original video file name
    
    # Filter impossible jumps using ear distance (should be a maximum of 70px)
    earDist = [] #empty list where all ear distances will go
    for index, row in df.iterrows():
        coord1 = (row.iloc[0], row.iloc[1]) #this gives coords for leftear
        coord2 = (row.iloc[3], row.iloc[4]) #this gives coords for rightear
        distance = math.dist(coord1, coord2) #calculate distance between coordinates
        earDist.append(distance) #store distance into array
    df["earDist"] = earDist #create a new column with ear distances
    df = df.drop(df[df.earDist > 70].index) #omit all rows/frames where distance > 70px (most likely an impossible jump occured)
    
    # Filter impossible jumps using back distance (should be a maximum of 110px)
    backDist = [] #empty list where all back distances will go
    for index, row in df.iterrows():
        coord1 = (row.iloc[9], row.iloc[10]) #this gives coords for midsection
        coord2 = (row.iloc[12], row.iloc[13]) #this gives coords for tail
        distance = math.dist(coord1, coord2) #calculate distance between coordinates
        backDist.append(distance) #store distance into array
    df["backDist"] = backDist #create a new column with back distances
    df = df.drop(df[df.backDist > 110].index) #omit all rows/frames where distance > 110px
    
    # Plot heat map
    x1 = df.iloc[range(0, len(df)),0] #leftear x
    x2 = df.iloc[range(0, len(df)),3] #rightear x
    y1 = df.iloc[range(0, len(df)),1] #leftear y
    y2 = df.iloc[range(0, len(df)),4] #rightear y

    xmid = (x1+x2)/2 #get midpoint of x-coordinates
    ymid = (y1+y2)/2 #get midpoint of y-coordinates

    plt.figure() #reset
    plt.hist2d(xmid, ymid, bins=100) #plot heatmap
    plt.colorbar() #legend
    # the next lines will plot gridlines to determine each region
    plt.plot([640/3,640/3],[0,480], color="silver", lw=0.5)
    plt.plot([1280/3,1280/3],[0,480], color="silver", lw=0.5)
    plt.plot([0,640],[480/3,480/3], color="silver", lw=0.5)
    plt.plot([0,640],[960/3,960/3], color="silver", lw=0.5)
    plt.title("Mouse " + str(leverData["mouseNum"][i]))
    plt.savefig(saveLoc + saveName + ".png", bbox_inches="tight") #save plot
    
    # save midpoint coordinates to appropriate lever group
    for index, row in leverData.iterrows():
        if leverData["lever"][index] == "L":
            xLeft = xLeft + xmid.tolist()
            yLeft = yLeft + ymid.tolist()
        if leverData["lever"][index] == "R":
            xRight = xRight + xmid.tolist()
            yRight = yRight + ymid.tolist()
            
# plot group heat maps
# first: according to reinforced lever
# left lever
plt.figure() #reset
plt.hist2d(xLeft, yLeft, bins=100) #plot heatmap
plt.colorbar() #legend
# the next lines will plot gridlines to determine each region
plt.plot([640/3,640/3],[0,480], color="silver", lw=0.5)
plt.plot([1280/3,1280/3],[0,480], color="silver", lw=0.5)
plt.plot([0,640],[480/3,480/3], color="silver", lw=0.5)
plt.plot([0,640],[960/3,960/3], color="silver", lw=0.5)
plt.title("Left reinforced lever mice group")
plt.savefig(saveLoc + "leftLever.png", bbox_inches="tight") #save plot

# right lever
plt.figure() #reset
plt.hist2d(xRight, yRight, bins=100) #plot heatmap
plt.colorbar() #legend
# the next lines will plot gridlines to determine each region
plt.plot([640/3,640/3],[0,480], color="silver", lw=0.5)
plt.plot([1280/3,1280/3],[0,480], color="silver", lw=0.5)
plt.plot([0,640],[480/3,480/3], color="silver", lw=0.5)
plt.plot([0,640],[960/3,960/3], color="silver", lw=0.5)
plt.title("Right reinforced lever mice group")
plt.savefig(saveLoc + "rightLever.png", bbox_inches="tight") #save plot

# then all data (combined)
xAll = xLeft + xRight #combine both groups' x coordinates
yAll = yLeft + yRight #combine both groups' y coordinates
plt.figure() #reset
plt.hist2d(xAll, yAll, bins=100) #plot heatmap
plt.colorbar() #legend
# the next lines will plot gridlines to determine each region
plt.plot([640/3,640/3],[0,480], color="silver", lw=0.5)
plt.plot([1280/3,1280/3],[0,480], color="silver", lw=0.5)
plt.plot([0,640],[480/3,480/3], color="silver", lw=0.5)
plt.plot([0,640],[960/3,960/3], color="silver", lw=0.5)
plt.title("All mice")
plt.savefig(saveLoc + "allMice.png", bbox_inches="tight") #save plot