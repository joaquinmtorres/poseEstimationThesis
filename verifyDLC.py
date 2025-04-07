# -*- coding: utf-8 -*-
"""
Created on Fri Apr  4 10:34:54 2025

@author: joaquinmtorres

Verifying effectiveness of DLC by looking at trajectory plots and their smoothness
as well as speed of mice.
"""

# import modules
import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np 

# determine files
file = "C:/Users/PCVR_103C/Desktop/Joaquin Thesis/trimmedDay4/20211115_Mouse 26_FR1 Day 4_gsDLC_Resnet50_secondStepFeb20shuffle1_snapshot_200.h5"
saveLoc = "C:/Users/PCVR_103C/Desktop/Joaquin Thesis/trimmedDay4/results/"
df = pd.read_hdf(file)


# get coordinates of midpoint of ears (head)
x1 = df.iloc[range(0, len(df)),0] #leftear x
x2 = df.iloc[range(0, len(df)),3] #rightear x
y1 = df.iloc[range(0, len(df)),1] #leftear y
y2 = df.iloc[range(0, len(df)),4] #rightear y

xmid = (x1+x2)/2 #get midpoint of x-coordinates
ymid = (y1+y2)/2 #get midpoint of y-coordinates

# plot trajectorty of head
plt.figure()
plt.plot(xmid, ymid)
plt.xlim([0, 640])
plt.ylim([0, 480])
plt.title('Head trajectory - initial')
plt.savefig(saveLoc + "trajInit.png", bbox_inches="tight")

# calculate smoothness of trajectory
initTraj = pd.DataFrame({"x": xmid, "y":ymid}) #concatenate into a dataframe
diffsInit = [] #this is where standard deviations will go
for i in range(0, len(initTraj)-1):
    coord1 = (initTraj["x"][i], initTraj["y"][i]) #first frame/point
    coord2 = (initTraj["x"][i+1], initTraj["y"][i+1]) #subsequent frame/point
    difference = math.dist(coord1, coord2) #calculate difference between the two coords
    diffsInit.append(difference)
# calculate standard deviations
stdevInit = np.std(diffsInit)


# filter out impossible jumps
# Filter impossible jumps using ear distance (should be a maximum of 70px)
earDist = [] #empty list where all ear distances will go
for index, row in df.iterrows():
    coord1 = (row.iloc[0], row.iloc[1]) #this gives coords for leftear
    coord2 = (row.iloc[3], row.iloc[4]) #this gives coords for rightear
    distance = math.dist(coord1, coord2) #calculate distance between coordinates
    earDist.append(distance) #store distance into array
df["earDist"] = earDist #create a new column with ear distances
df = df.drop(df[df.earDist > 70].index) #omit all rows/frames where distance > 70px (most likely an impossible jump occured)
df = df.reset_index(drop=True)

# Filter impossible jumps using back distance (should be a maximum of 110px)
backDist = [] #empty list where all back distances will go
for index, row in df.iterrows():
    coord1 = (row.iloc[9], row.iloc[10]) #this gives coords for midsection
    coord2 = (row.iloc[12], row.iloc[13]) #this gives coords for tail
    distance = math.dist(coord1, coord2) #calculate distance between coordinates
    backDist.append(distance) #store distance into array
df["backDist"] = backDist #create a new column with back distances
df = df.drop(df[df.backDist > 110].index) #omit all rows/frames where distance > 110px
df = df.reset_index(drop=True)

# get coordinates of midpoint of ears (head)
x1 = df.iloc[range(0, len(df)),0] #leftear x
x2 = df.iloc[range(0, len(df)),3] #rightear x
y1 = df.iloc[range(0, len(df)),1] #leftear y
y2 = df.iloc[range(0, len(df)),4] #rightear y

xmid = (x1+x2)/2 #get midpoint of x-coordinates
ymid = (y1+y2)/2 #get midpoint of y-coordinates

# plot trajectorty of head
plt.figure()
plt.plot(xmid, ymid)
plt.xlim([0, 640])
plt.ylim([0, 480])
plt.title('Head trajectory - cleaned')
plt.savefig(saveLoc + "trajClean.png", bbox_inches="tight")

# calculate smoothness of trajectory
cleanTraj = pd.DataFrame({"x": xmid, "y":ymid}) #concatenate into a dataframe
diffsClean = [] #this is where standard deviations will go
for j in range(0, len(cleanTraj)-1):
    coord1 = (cleanTraj["x"][j], cleanTraj["y"][j]) #first frame/point
    coord2 = (cleanTraj["x"][j+1], cleanTraj["y"][j+1]) #subsequent frame/point
    difference = math.dist(coord1, coord2) #calculate difference between the two coords
    diffsClean.append(difference)
# calculate standard deviations
stdevClean = np.std(diffsClean)


# SuperAnimal/Model Zoo trajectory - we're looking at the neck marker because it's closest to our ear midpoint in the regular network
modelZoo = pd.read_hdf("C:/Users/PCVR_103C/Desktop/Joaquin Thesis/verifyDLC/20211115_Mouse 26_FR1 Day 4_gs_superanimal_topviewmouse_fasterrcnn_resnet50_fpn_v2_resnet_50.h5")
# drop undetected frames (i.e. when coordinates == -1)
xNeck = modelZoo.iloc[range(0, len(modelZoo)), 21].to_list()
yNeck = modelZoo.iloc[range(0, len(modelZoo)), 22].to_list()
dfMZ = pd.DataFrame({"x": xNeck, "y": yNeck})
dfMZ = dfMZ.drop(dfMZ[dfMZ.x < 0].index)
dfMZ = dfMZ.reset_index(drop=True)
t = np.arange(len(dfMZ))
# verify trajectory plots make sense
plt.figure()
plt.scatter(dfMZ.iloc[range(0, len(dfMZ)),0], dfMZ.iloc[range(0, len(dfMZ)),1], c=t)
plt.xlim([0, 640])
plt.ylim([0, 480])
plt.title('Neck trajectory - Animal Zoo')
plt.savefig(saveLoc + "trajMZ.png", bbox_inches="tight")

# calculate smoothness of trajectory
mzTraj = pd.DataFrame({"x": xNeck, "y":yNeck}) #concatenate into a dataframe
diffsMZ = [] #this is where standard deviations will go
for k in range(0, len(mzTraj)-1):
    coord1 = (mzTraj["x"][k], mzTraj["y"][k]) #first frame/point
    coord2 = (mzTraj["x"][k+1], mzTraj["y"][k+1]) #subsequent frame/point
    difference = math.dist(coord1, coord2) #calculate difference between the two coords
    diffsMZ.append(difference)
# calculate standard deviations
stdevMZ = np.std(diffsMZ)


# create plots
# smoothness
dfSmoothness = pd.DataFrame({"Trajectory": ["Initial", "Clean", "Model Zoo"], "Smoothness": [stdevInit, stdevClean, stdevMZ]})
plt.figure()
plt.plot(dfSmoothness["Trajectory"], dfSmoothness["Smoothness"])
plt.xlabel("Trajectory")
plt.ylabel("Variance in movement per frame (px)")
plt.ylim(0, 150)
plt.savefig(saveLoc + "smoothness.png", bbox_inches="tight")

# speed of mice
dfSpeed = pd.DataFrame({"Trajectory": ["Initial", "Clean", "Model Zoo"], "Speed": [np.mean(diffsInit), np.mean(diffsClean), np.mean(diffsMZ)], "SEM": [stdevInit/math.sqrt(len(diffsInit)), stdevClean/math.sqrt(len(diffsClean)), stdevMZ/math.sqrt(len(diffsMZ))]})
plt.figure()
plt.plot(dfSpeed["Trajectory"], dfSpeed["Speed"])
plt.errorbar(dfSpeed["Trajectory"], dfSpeed["Speed"], yerr=dfSpeed["SEM"], capsize=3, fmt="r--o", ecolor="black")
plt.xlabel("Trajectory")
plt.ylabel("Average speed of mouse (px/frame)")
plt.axhline(34, linestyle="--")
plt.ylim(0, 50)
plt.savefig(saveLoc + "speed.png", bbox_inches="tight")