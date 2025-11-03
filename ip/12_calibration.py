import numpy as np
import cv2 as cv
import glob
import json
CHECKERBOARD = (6, 9)
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)

objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)


objpoints = []
imgpoints = []
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

        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)

        cv.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(0)
h, w = img.shape[:2]
ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, (w, h), None, None)

with open("resource/calibration.json", 'w', encoding='utf-8') as f:

        json.dump({
            "reprojection_error": ret,
            "camera_matrix": mtx.tolist(),
            "distortion_coefficients": dist.tolist(),
            "rotation_vectors": [rvec.tolist() for rvec in rvecs],
            "translation_vectors": [tvec.tolist() for tvec in tvecs],
            "points": objp.tolist()
        }, f, indent=4)
print(ret, mtx, dist, rvecs, tvecs)
