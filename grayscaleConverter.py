# -*- coding: utf-8 -*-
"""
Created on Sun Feb 16 12:08:06 2025

@author: joaquinmtorres

converting phys psych videos to grayscale for analysis (thesis)

Sources:
    https://www.geeksforgeeks.org/converting-color-video-to-grayscale-using-opencv-in-python/
    https://stackoverflow.com/questions/64775951/how-to-convert-a-rgb-video-to-grayscale-and-save-it
    ChatGPT - troubleshooting code (particularly when saving files)
"""

#import modules
import cv2
import os
import os.path
import glob

#determine location of files
videosLoc = "/Users/PCVR_103C/Desktop/Joaquin Thesis/Raw Files/"
vidList = sorted(glob.glob(videosLoc + "*.mp4")) #sorts all videos
saveLoc = "/Users/PCVR_103C/Desktop/Joaquin Thesis/GS Files/"

#start for loop
for video in (vidList):
    saveName = video.split("/")[-1].split("\\")[-1][:-4] + "_gs" #take file name, add grayscale label

    source = cv2.VideoCapture(video) #read video
    
    # Set resolutions
    frame_width  = int(source.get(3))
    frame_height = int(source.get(4))
    size = (frame_width, frame_height)
    
    result = cv2.VideoWriter(os.path.join(saveLoc, saveName +  ".mp4"), cv2.VideoWriter_fourcc(*"mp4v"), 10, size, 0)

    #run loop to grayscale each frame
    while True:
        ret, img = source.read() #extract frames
        if not ret:
            break #break if no more frames
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #convert to grayscale
        result.write(gray) #write to grayscale
        
    # Save
    cv2.destroyAllWindows()
    source.release()
    result.release()
    