import cv2
import numpy as np
import json
import os
CHECKERBOARD = (6, 9)

objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

objp[:, 0] -= ((CHECKERBOARD[0] - 1)) / 2.0
objp[:, 1] -= ((CHECKERBOARD[1] - 1)) / 2.0

def load_camera_params(filepath="camera_params.json"):
    if not os.path.exists(filepath):
        return None, None
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        

        camera_matrix = np.array(data["camera_matrix"], dtype=np.float32)
        dist_coeffs = np.array(data["distortion_coefficients"], dtype=np.float32)
        
        return camera_matrix, dist_coeffs
    except Exception as e:
        return None, None
def draw_axes(img, rvec, tvec, K, dist, length=4):
    axis = np.float32([[0, 0, 0], [length, 0, 0], [0, length, 0], [0, 0, length]]).reshape(-1, 3)

    imgpts, jac = cv2.projectPoints(axis, rvec, tvec, K, dist)
    imgpts = np.int32(imgpts).reshape(-1, 2)
    origin = tuple(imgpts[0].ravel())
    

    img = cv2.line(img, origin, tuple(imgpts[1].ravel()), (0, 0, 255), 5)

    img = cv2.line(img, origin, tuple(imgpts[2].ravel()), (0, 255, 0), 5)

    img = cv2.line(img, origin, tuple(imgpts[3].ravel()), (255, 0, 0), 5)
    

    cv2.putText(img, "X", tuple(imgpts[1].ravel()), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
    cv2.putText(img, "Y", tuple(imgpts[2].ravel()), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
    cv2.putText(img, "Z", tuple(imgpts[3].ravel()), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)
    
    return img

def main():

    K, dist = load_camera_params("resource/calibration.json")
    if K is None:
        return
    img = cv2.imread('./resource/target_frame.jpg')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    img_width, img_height = img.shape[1], img.shape[0]

    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

    if ret:

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        image_points = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

        (success, rvec, tvec) = cv2.solvePnP(
            objp, 
            image_points, 
            K, 
            dist,
            flags=cv2.SOLVEPNP_ITERATIVE
        )

        if success:
            

            img_with_axes = draw_axes(img, rvec, tvec, K, dist)
            cv2.imshow("PnP Result: Chessboard Corner Detection and Pose Estimation", img_with_axes)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        else:
            print("\n--- PnP Result ---")
            print("PnP failed. Sufficient corners detected but algorithm did not converge.")

    else:

        print("\n--- Corner Detection Failed ---")


if __name__ == "__main__":
    main()
