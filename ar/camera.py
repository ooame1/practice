import json
import os
import cv2
import numpy as np

def create_world_points(board_size):
    objp = np.zeros((board_size[0] * board_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:board_size[0], 0:board_size[1]].T.reshape(-1, 2)
    objp[:, 0] -= ((board_size[0] - 1)) / 2.0
    objp[:, 1] -= ((board_size[1] - 1)) / 2.0
    return objp

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

def detect_extrinsics(img, world_points = create_world_points((6,9))):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)
    rvec, tvec = None, None

    if ret:
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        image_points = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

        (success, rvec, tvec) = cv2.solvePnP(
            world_points, 
            image_points, 
            CAMERA_MATRIX,
            DIST_COEFFS,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        if success:
            return True, rvec, tvec
    return False, None, None

def intrinsic2projection(K):

    W = 1920.0
    H = 1080.0
    N = 0.1
    F = 100.0
    fx = K[0, 0]
    fy = K[1, 1]
    cx = K[0, 2]
    cy = K[1, 2]
    P_00 = 2.0 * fx / W
    P_02 = 1.0 - 2.0 * cx / W
    P_11 = 2.0 * fy / H
    P_12 = 2.0 * cy / H - 1.0

    P_22 = -(F + N) / (F - N)
    P_23 = -2.0 * F * N / (F - N)
    P_32 = -1.0
    P_33 = 0.0
    return np.array([
        [P_00, 0.0, P_02, 0.0],
        [0.0, P_11, P_12, 0.0],
        [0.0, 0.0, P_22, P_23],
        [0.0, 0.0, P_32, P_33]
    ], dtype=np.float32)

def extrinsic2ViewMatrix(rvec, tvec):
    R, _ = cv2.Rodrigues(rvec)
    
    Rx = np.array([
        [1.0, 0.0, 0.0],
        [0.0, -1.0, 0.0],
        [0.0, 0.0, -1.0]
    ], dtype=np.float32)

    TVEC_flat = tvec.flatten()

    R_t_3x4 = np.hstack((R, TVEC_flat.reshape((3, 1))))

    transform_matrix_3x4 = Rx @ R_t_3x4

    M_np = np.eye(4, dtype=np.float32)
    M_np[:3, :] = transform_matrix_3x4

    return M_np

CHECKERBOARD = (6, 9)
WORLD_POINTS = create_world_points(CHECKERBOARD)
CAMERA_MATRIX, DIST_COEFFS = load_camera_params("resource/calibration.json")
CAMERA_DEVICE_INDEX = 1
Projection = intrinsic2projection(CAMERA_MATRIX)