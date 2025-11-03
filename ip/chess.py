import numpy as np
import cv2 as cv
import glob

CHECKERBOARD = (8, 5) 
SQUARE_SIZE = 20
CRITERIA = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objpoints = []

imgpoints = [] 
objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)

objp[0, :, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

objp = objp * SQUARE_SIZE
CAP_DEVICE = 0
cap = cv.VideoCapture(CAP_DEVICE)
if not cap.isOpened():
    exit()

CALIBRATION_FRAMES = 15
frames_collected = 0

while frames_collected < CALIBRATION_FRAMES:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    ret_find, corners = cv.findChessboardCorners(gray, CHECKERBOARD, None)

    if ret_find:

        text_color = (0, 255, 0)
        

        corners_refined = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), CRITERIA)
        

        cv.drawChessboardCorners(frame, CHECKERBOARD, corners_refined, ret_find)
        

        prompt_text = "FOUND! Press 'S' to SAVE frame."
        if cv.waitKey(1) & 0xFF == ord('s'):
            objpoints.append(objp)
            imgpoints.append(corners_refined)
            frames_collected += 1

            cv.waitKey(500) 
            text_color = (255, 0, 0)

    else:
        prompt_text = "NOT FOUND. Adjust position."
        text_color = (0, 0, 255)
    cv.putText(frame, prompt_text, (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2, cv.LINE_AA)
    cv.putText(frame, f"Collected: {frames_collected}/{CALIBRATION_FRAMES}", (10, 60), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv.LINE_AA)
    
    cv.imshow('Calibration View', frame)
    

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
if frames_collected < 5:
    exit()

ret_cal, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
print("-" * 30)
if ret_cal:
    print(mtx)
    print(dist)
else:
    print("failed")
print("-" * 30)