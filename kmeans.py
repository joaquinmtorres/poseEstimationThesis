# -*- coding: utf-8 -*-
"""
Created on Fri Apr  4 10:18:56 2025

@author: joaquinmtorres

Using kmeans clustering to separate learner mice from non-learner mice, determining
a threshold of correct lever presses. Also generating heat maps just like
heatMaps.py, separating learners vs. non-learners.

kmeans clustering from https://www.w3schools.com/python/python_ml_k-means.asp
"""

# import modules
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
import glob
import numpy as np
import math

# set up data
csv = "C:/Users/PCVR_103C/Desktop/Joaquin Thesis/Code/mouseData.csv"
mouseData = pd.read_csv(csv)
saveLoc = "C:/Users/PCVR_103C/Desktop/Joaquin Thesis/trimmedDay4/results/"

# take necessary variables
y = mouseData['timeInR6'].to_list()
x = mouseData['correct'].to_list()

# initial plot
plt.figure()
plt.scatter(x, y)
plt.xlabel("Number of correct responses")
plt.ylabel("Proportion of time spend in region 6")
plt.savefig(saveLoc + "kmeansInit.png", bbox_inches="tight")

# elbow method to determine K values
data = list(zip(x, y))
inertias = []

for i in range(1,11):
    kmeans = KMeans(n_clusters=i)
    kmeans.fit(data)
    inertias.append(kmeans.inertia_)

plt.figure()    
plt.plot(range(1,11), inertias, marker='o')
plt.title('Elbow method')
plt.xlabel('Number of clusters')
plt.ylabel('Inertia')
plt.savefig(saveLoc + "kmeansElbow.png", bbox_inches="tight")
# elbow suggests 2 clusters

# retrain and visualize with K=2
kmeans = KMeans(n_clusters=2)
kmeans.fit(data)

plt.figure()
plt.scatter(x, y, c=kmeans.labels_)
plt.xlabel("Number of correct responses")
plt.ylabel("Proportion of time spend in region 6")
plt.savefig(saveLoc + "kmeansClusters.png", bbox_inches="tight")


# separating learners from non-learners
# determine location of h5 files and where results would be saved
fileLoc = "C:/Users/PCVR_103C/Desktop/Joaquin Thesis/trimmedDay4/"
fileList = sorted(glob.glob(fileLoc + "*.h5")) #sorts all h5 files

# concatenate all data into one dataframe
fileDF = pd.concat([pd.Series(fileList), mouseData["mouseNum"], mouseData["diet"], mouseData["lever"], mouseData['correct'], mouseData['timeInR6']], axis=1)

# set empty list to determine if learner or non-learner
learnType = []
# sort data
for index, row in fileDF.iterrows():
    if fileDF["correct"][index] <= 20:
        learnType.append("nonlearner")
    else:
        learnType.append("learner")
fileDF["learnType"] = learnType
fileDF.to_csv(saveLoc + "/fullData.csv", index=False)

# create empty lists to group by learnType and diet
HFDlearners = []
SClearners = []
HFDnonlearners = []
SCnonlearners = []

# create matrices
for j in range(len(fileDF[0])):
    file = fileDF[0][j]
    data = pd.read_hdf(file)
    
    # Filter impossible jumps using ear distance (should be a maximum of 70px)
    earDist = [] #empty list where all ear distances will go
    for index, row in data.iterrows():
        coord1 = (row.iloc[0], row.iloc[1]) #this gives coords for leftear
        coord2 = (row.iloc[3], row.iloc[4]) #this gives coords for rightear
        distance = math.dist(coord1, coord2) #calculate distance between coordinates
        earDist.append(distance) #store distance into array
    data["earDist"] = earDist #create a new column with ear distances
    data = data.drop(data[data.earDist > 70].index) #omit all rows/frames where distance > 70px (most likely an impossible jump occured)
    
   	# Filter impossible jumps using back distance (should be a maximum of 110px)
    backDist = [] #empty list where all back distances will go
    for index, row in data.iterrows():
        coord1 = (row.iloc[9], row.iloc[10]) #this gives coords for midsection
        coord2 = (row.iloc[12], row.iloc[13]) #this gives coords for tail
        distance = math.dist(coord1, coord2) #calculate distance between coordinates
       	backDist.append(distance) #store distance into array
    data["backDist"] = backDist #create a new column with back distances
    data = data.drop(data[data.backDist > 110].index) #omit all rows/frames where distance > 110px
    
    # Plot heat map
    x1 = data.iloc[range(0, len(data)),0] #leftear x
    x2 = data.iloc[range(0, len(data)),3] #rightear x
    y1 = data.iloc[range(0, len(data)),1] #leftear y
    y2 = data.iloc[range(0, len(data)),4] #rightear y

    xmid = (x1+x2)/2 #get midpoint of x-coordinates
    ymid = (y1+y2)/2 #get midpoint of y-coordinates

	# data for group heat maps
    plt.figure() #reset
    g = plt.hist2d(xmid, ymid, bins=15) #plot heatmap
    mat = g[0]/sum(sum(g[0])) #get ratios
    mat = np.rot90(mat) #rotate to correct
    # correct location of reinforced lever (region 3/top right)
    if mouseData["lever"][j] == "R":
        mat = np.flipud(mat)
    plt.close()
    
    # sort by diet group and learn type
    if fileDF["correct"][j] >= 20 and fileDF["diet"][j] == "HFD":
        HFDlearners.append(mat)
    if fileDF["correct"][j] >= 20 and fileDF["diet"][j] == "SC":
        SClearners.append(mat)
    if fileDF["correct"][j] < 20 and fileDF["diet"][j] == "HFD":
        HFDnonlearners.append(mat)
    if fileDF["correct"][j] < 20 and fileDF["diet"][j] == "SC":
        SCnonlearners.append(mat)

# plot heat maps
plt.figure()
# all learners
plt.subplot(3,2,1)
allLearners = sum(sum(HFDlearners), sum(SClearners))/(len(HFDlearners)+len(SClearners)) #get average proportion time spent
plt.imshow(allLearners, cmap="hot", interpolation="nearest", extent=[0,640,0,480])
plt.title("All learners")
plt.plot([640/3,640/3],[0,480], color="silver", lw=0.5)
plt.plot([1280/3,1280/3],[0,480], color="silver", lw=0.5)
plt.plot([0,640],[480/3,480/3], color="silver", lw=0.5)
plt.plot([0,640],[960/3,960/3], color="silver", lw=0.5)
plt.colorbar()
plt.clim(0, 0.13)

# all nonlearners
plt.subplot(3,2,2)
allNonlearners = sum(sum(HFDnonlearners), sum(SCnonlearners))/(len(HFDnonlearners)+len(SCnonlearners))
plt.imshow(allNonlearners, cmap="hot", interpolation="nearest", extent=[0,640,0,480])
plt.title("All non-learners")
plt.plot([640/3,640/3],[0,480], color="silver", lw=0.5)
plt.plot([1280/3,1280/3],[0,480], color="silver", lw=0.5)
plt.plot([0,640],[480/3,480/3], color="silver", lw=0.5)
plt.plot([0,640],[960/3,960/3], color="silver", lw=0.5)
plt.colorbar()
plt.clim(0, 0.13)

# HFD learners
plt.subplot(3,2,3)
HFDlearnMat = sum(HFDlearners)/len(HFDlearners)
plt.imshow(HFDlearnMat, cmap="hot", interpolation="nearest", extent=[0,640,0,480])
plt.title("HFD learners")
plt.plot([640/3,640/3],[0,480], color="silver", lw=0.5)
plt.plot([1280/3,1280/3],[0,480], color="silver", lw=0.5)
plt.plot([0,640],[480/3,480/3], color="silver", lw=0.5)
plt.plot([0,640],[960/3,960/3], color="silver", lw=0.5)
plt.colorbar()
plt.clim(0, 0.06)

# SC learners
plt.subplot(3,2,4)
SClearnMat = sum(SClearners)/len(SClearners)
plt.imshow(SClearnMat, cmap="hot", interpolation="nearest", extent=[0,640,0,480])
plt.title("SC learners")
plt.plot([640/3,640/3],[0,480], color="silver", lw=0.5)
plt.plot([1280/3,1280/3],[0,480], color="silver", lw=0.5)
plt.plot([0,640],[480/3,480/3], color="silver", lw=0.5)
plt.plot([0,640],[960/3,960/3], color="silver", lw=0.5)
plt.colorbar()
plt.clim(0, 0.06)

# HFD non-learners
plt.subplot(3,2,5)
HFDnonMat = sum(HFDnonlearners)/len(HFDnonlearners)
plt.imshow(HFDnonMat, cmap="hot", interpolation="nearest", extent=[0,640,0,480])
plt.title("HFD non-learners")
plt.plot([640/3,640/3],[0,480], color="silver", lw=0.5)
plt.plot([1280/3,1280/3],[0,480], color="silver", lw=0.5)
plt.plot([0,640],[480/3,480/3], color="silver", lw=0.5)
plt.plot([0,640],[960/3,960/3], color="silver", lw=0.5)
plt.colorbar()
plt.clim(0, 0.06)

# SC non-learners
plt.subplot(3,2,6)
SCnonMat = sum(SCnonlearners)/len(SCnonlearners)
plt.imshow(SCnonMat, cmap="hot", interpolation="nearest", extent=[0,640,0,480])
plt.title("SC non-learners")
plt.plot([640/3,640/3],[0,480], color="silver", lw=0.5)
plt.plot([1280/3,1280/3],[0,480], color="silver", lw=0.5)
plt.plot([0,640],[480/3,480/3], color="silver", lw=0.5)
plt.plot([0,640],[960/3,960/3], color="silver", lw=0.5)
plt.colorbar()
plt.clim(0, 0.06)

plt.tight_layout() # adjust spacing
plt.savefig(saveLoc + "learnTypes.png", bbox_inches="tight")