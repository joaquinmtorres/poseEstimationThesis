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
import numpy as np

# determine location of h5 files and where results would be saved
fileLoc = "C:/Users/PCVR_103C/Desktop/Joaquin Thesis/trimmedDay4/"
fileList = sorted(glob.glob(fileLoc + "*.h5")) #sorts all h5 files
saveLoc = "C:/Users/PCVR_103C/Desktop/Joaquin Thesis/trimmedDay4/results/"
# reinforced lever data
mouseData = pd.read_csv("C:/Users/PCVR_103C/Desktop/Joaquin Thesis/Code/mouseData.csv")


# functions
# from: https://www.geeksforgeeks.org/how-to-create-boxplots-by-group-in-matplotlib/
# each plot returns a dictionary, use plt.setp()
# function to assign the color code
# for all properties of the box plot of particular group
# use the below function to set color for particular group,
# by iterating over all properties of the box plot
def define_box_properties(plot_name, color_code, label):
    for k, v in plot_name.items():
        plt.setp(plot_name.get(k), color=color_code)
         
    # use plot function to draw a small line to name the legend.
    plt.plot([], c=color_code, label=label)
    plt.legend()


# set empty variable for matrix collecting all matrices for place preference (bins=9)
prefMatsHFD = []
dfPrefHFD = pd.DataFrame(index=np.arange(9)+1)
prefMatsSC = []
dfPrefSC = pd.DataFrame(index=np.arange(9)+1)
# set empty variable for matrix collecting all matrices for collective heat map (bins=15)
heatHFD = []
dfHeatHFD = pd.DataFrame(index=np.arange(15)+1)
heatSC = []
dfHeatSC = pd.DataFrame(index=np.arange(15)+1)


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
    

    # individual plot
    plt.figure() #reset
    plt.hist2d(xmid, ymid, bins=100) #plot heatmap
    plt.colorbar() #legend
    # the next lines will plot gridlines to determine each region
    plt.plot([640/3,640/3],[0,480], color="silver", lw=0.5)
    plt.plot([1280/3,1280/3],[0,480], color="silver", lw=0.5)
    plt.plot([0,640],[480/3,480/3], color="silver", lw=0.5)
    plt.plot([0,640],[960/3,960/3], color="silver", lw=0.5)
    plt.title("Mouse " + str(mouseData["mouseNum"][i]))
    plt.savefig(saveLoc + saveName + ".png", bbox_inches="tight") #save plot
    
    # data for place preference plot
    plt.figure()
    h = plt.hist2d(xmid, ymid, bins=3) #save to a variable h
    mat1 = h[0]/sum(sum(h[0])) #get ratios for matrix
    mat1 = np.rot90(mat1) #rotate mat so it follows the regions
    # correct location of reinforced lever (region 3/top right)
    if mouseData["lever"][i] == "R":
        mat1 = np.flipud(mat1)
    mat1 = mat1.flatten() #convert to 1D array according to region number
    # add to appropriate array
    if mouseData["diet"][i] == "HFD":
        prefMatsHFD.append(mat1)
        dfPrefHFD["Mouse" + str(i+1)] = mat1
    if mouseData["diet"][i] == "SC":
        prefMatsSC.append(mat1)
        dfPrefSC["mouse" + str(i+1)] = mat1
    plt.close()        
        
    # data for group heat maps
    plt.figure() #reset
    g = plt.hist2d(xmid, ymid, bins=15) #plot heatmap
    mat2 = g[0]/sum(sum(g[0])) #get ratios
    mat2 = np.rot90(mat2) #rotate to correct
    # correct location of reinforced lever (region 3/top right)
    if mouseData["lever"][i] == "R":
        mat2 = np.flipud(mat2)
    if mouseData["diet"][i] == "HFD":
        heatHFD.append(mat2)
        #mat2 = mat2.flatten()
        #dfHeatHFD["mouse" + str(i+1)] = mat2
    if mouseData["diet"][i] == "SC":
        heatSC.append(mat2)
        #mat2 = mat2.flatten()
        #dfHeatSC["mouse" + str(i+1)] = mat2
    plt.close()


# process data frames
dfPrefHFD["Mean"] = dfPrefHFD.mean(axis=1)
dfPrefHFD["SEM"] = dfPrefHFD.iloc[:,:-1].sem(axis=1)
dfPrefHFD.to_csv(saveLoc + "/placePrefHFD.csv", index=False)
dfPrefSC["Mean"] = dfPrefSC.mean(axis=1)
dfPrefSC["SEM"] = dfPrefSC.iloc[:,:-1].sem(axis=1)
dfPrefSC.to_csv(saveLoc + "/placePrefSC.csv", index=False)
# plot group data
# first: place preference
# set data
prefHFD = pd.read_csv("C:/Users/PCVR_103C/Desktop/Joaquin Thesis/trimmedDay4/results/placePrefHFD.csv")
prefMeanHFD = prefHFD["Mean"]
prefSemHFD = prefHFD["SEM"]
prefSC = pd.read_csv("C:/Users/PCVR_103C/Desktop/Joaquin Thesis/trimmedDay4/results/placePrefSC.csv")
prefMeanSC = prefSC["Mean"]
prefSemSC = prefSC["SEM"]
regions = np.arange(9)+1 #set regions
# create plot
plt.figure()
plt.bar(regions-0.2, prefMeanHFD, color="#FFC20A", width=0.4, label = "HFD")
plt.errorbar(regions-0.2, prefMeanHFD, yerr=prefSemHFD, fmt=".", color="black")
plt.bar(regions+0.2, prefMeanSC, color="#0C7BDC", width=0.4, label = "SC")
plt.errorbar(regions+0.2, prefMeanSC, yerr=prefSemSC, fmt=".", color="black")
plt.xlabel("Region")
plt.xticks(regions)
plt.ylabel("Proportion of time spent")
plt.title("Regional dwell time")
plt.legend()
plt.savefig(saveLoc + "rdt.png", bbox_inches="tight") #save plot


# second: heat maps (bins=15)
# set data
aveHeatHFD = sum(heatHFD)/len(heatHFD)
matHeatHFD = np.matrix(aveHeatHFD)
aveHeatSC = sum(heatSC)/len(heatSC)
matHeatSC = np.matrix(aveHeatSC)
# plot
plt.figure()
plt.subplot(1,2,1)
plt.imshow(matHeatHFD, cmap="hot", interpolation="nearest", extent=[0,640,0,480])
plt.title("HFD")
plt.plot([640/3,640/3],[0,480], color="silver", lw=0.5)
plt.plot([1280/3,1280/3],[0,480], color="silver", lw=0.5)
plt.plot([0,640],[480/3,480/3], color="silver", lw=0.5)
plt.plot([0,640],[960/3,960/3], color="silver", lw=0.5)
plt.colorbar(location = "bottom")
plt.subplot(1,2,2)
plt.imshow(matHeatSC, cmap="hot", interpolation="nearest", extent=[0,640,0,480])
plt.title("SC")
plt.plot([640/3,640/3],[0,480], color="silver", lw=0.5)
plt.plot([1280/3,1280/3],[0,480], color="silver", lw=0.5)
plt.plot([0,640],[480/3,480/3], color="silver", lw=0.5)
plt.plot([0,640],[960/3,960/3], color="silver", lw=0.5)
plt.colorbar(location = "bottom")
plt.savefig(saveLoc + "allHeat.png", bbox_inches="tight")


# third: time in each location of interest
# from RDT data, take each value (time ratio) spent in region 3 (reinforced lever), 6 (hopper) and 9 (unreinforced lever)
reg3HFD = prefHFD.iloc[2][:-2].to_numpy()
reg3SC = prefSC.iloc[2][:-2].to_numpy()
reg6HFD = prefHFD.iloc[5][:-2].to_numpy()
reg6SC = prefSC.iloc[5][:-2].to_numpy()
reg9HFD = prefHFD.iloc[8][:-2].to_numpy()
reg9SC = prefSC.iloc[8][:-2].to_numpy()

regHFD = [reg3HFD, reg6HFD, reg9HFD]
regSC = [reg3SC, reg6SC, reg9SC]
ticks = [3,6,9]

plt.figure()
regHFDplot = plt.boxplot(regHFD, positions=np.array(np.arange(len(regHFD)))*2.0-0.35, widths=0.6)
regSCplot = plt.boxplot(regSC, positions=np.array(np.arange(len(regSC)))*2.0+0.35,widths=0.6)
define_box_properties(regHFDplot, "#FFC20A", "HFD")
define_box_properties(regSCplot, "#0C7BDC", "SC")
plt.xticks(np.arange(0, len(ticks) * 2, 2), ticks)
plt.xlim(-2, len(ticks)*2)
plt.ylim(0, 1.0)
plt.title
plt.xlabel("Region")
plt.ylabel("Proportion of time spent")
plt.title("Time spent in each region of interest")
plt.savefig(saveLoc + "timeRegion.png", bbox_inches="tight")


# last: weight correlation
weightHFD = []
weightSC = []
#sort data
for index, row in mouseData.iterrows():
    if mouseData["diet"][index] == "HFD":
        weightHFD.append(mouseData["weight"][index])
    if mouseData["diet"][index] == "SC":
        weightSC.append(mouseData["weight"][index])
#sort in ascending order
weightHFD = np.sort(weightHFD)
weightSC = np.sort(weightSC)
#plot
plt.figure()
plt.scatter(weightHFD, reg3HFD, label = "HFD - reinforced lever", color = "yellow")
m1, b1 = np.polyfit(weightHFD, reg3HFD, 1)
plt.plot(weightHFD, m1*weightHFD+b1, color = "yellow")
plt.scatter(weightSC, reg3SC, label = "SC - reinforced lever", color = "dodgerblue")
m2, b2 = np.polyfit(weightHFD, reg3SC, 1)
plt.plot(weightHFD, m2*weightHFD+b2, color = "dodgerblue")
plt.scatter(weightHFD, reg6HFD, label = "HFD - hopper", color = "gold")
m3, b3 = np.polyfit(weightHFD, reg6HFD, 1)
plt.plot(weightHFD, m3*weightHFD+b3, color = "gold")
plt.scatter(weightSC, reg6SC, label = "SC - hopper", color = "blue")
m4, b4 = np.polyfit(weightHFD, reg6SC, 1)
plt.plot(weightHFD, m4*weightHFD+b4, color = "blue")
plt.scatter(weightHFD, reg9HFD, label = "HFD - unreinforced lever", color = "khaki")
m5, b5 = np.polyfit(weightHFD, reg9HFD, 1)
plt.plot(weightHFD, m5*weightHFD+b5, color = "khaki")
plt.scatter(weightSC, reg9SC, label = "SC - unreinforced lever", color = "lightskyblue")
m6, b6 = np.polyfit(weightHFD, reg9SC, 1)
plt.plot(weightHFD, m6*weightHFD+b6, color = "lightskyblue")
plt.title("Correlation between weight and time spent in ROIs")
plt.xlabel("Weight (g)")
plt.ylabel("Proportion of time spent")
plt.legend(loc = "upper right", fontsize="x-small")
plt.savefig(saveLoc + "weightCorr.png", bbox_inches="tight")