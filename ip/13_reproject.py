import numpy as np
import cv2 as cv
import glob
import json
CHECKERBOARD = (6, 9)
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)

objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
objpoints = []
imgpoints = []
imgs = []
COLOR = (0, 255, 0) 
RADIUS = 10
THICKNESS = -1
images = glob.glob('./resource/calibration_images/*.jpg')

for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ret, corners = cv.findChessboardCorners(gray, CHECKERBOARD, None)

    if ret == False:
        cv.imshow('img', gray)
        cv.waitKey(0)
        continue

    if ret == True:
        objpoints.append(objp)
        imgs.append(img)
        

        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)
h, w = img.shape[:2]
ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, (w, h), None, None)

for i in range(len(objpoints)):
    p = objpoints[i]
    reprojected_points, _ = cv.projectPoints(
        p, 
        rvecs[i], 
        tvecs[i], 
        mtx, 
        dist
    )
    reprojected_points = reprojected_points.reshape(-1, 2)
    img = imgs[i]
    for point in reprojected_points:

        center_x = int(round(point[0]))
        center_y = int(round(point[1]))
        if 0 <= center_x < w and 0 <= center_y < h:
            cv.circle(img, (center_x, center_y), RADIUS, COLOR, THICKNESS)
    cv.imshow('Reprojected Points', img)
    cv.waitKey(0)
