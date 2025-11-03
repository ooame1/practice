import cv2
import glfw
import numpy as np
import pyrr
import math

def get_view_matrix():
    return ViewMatrix

def get_projection_matrix():
    return ProjectionMatrix

def compute_matrices_from_inputs(window):
    global ViewMatrix, ProjectionMatrix, position, horizontalAngle, verticalAngle, last_time
    
    currentTime = glfw.get_time()
    
    if last_time == 0.0:
        last_time = currentTime

    deltaTime = float(currentTime - last_time)

    xpos, ypos = glfw.get_cursor_pos(window)

    glfw.set_cursor_pos(window, 1024 / 2, 768 / 2)

    horizontalAngle += mouseSpeed * float(1024 / 2 - xpos)
    verticalAngle += mouseSpeed * float(768 / 2 - ypos)

    direction = pyrr.Vector3([
        math.cos(verticalAngle) * math.sin(horizontalAngle),
        math.sin(verticalAngle),
        math.cos(verticalAngle) * math.cos(horizontalAngle)
    ])
    
    right = pyrr.Vector3([
        math.sin(horizontalAngle - math.pi / 2.0),
        0,
        math.cos(horizontalAngle - math.pi / 2.0)
    ])
    
    up = pyrr.vector3.cross(right, direction)

    if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
        position += direction * deltaTime * speed
    
    if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
        position -= direction * deltaTime * speed
    
    if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
        position += right * deltaTime * speed
    
    if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
        position -= right * deltaTime * speed

    FoV = initialFoV

    ProjectionMatrix = pyrr.Matrix44.perspective_projection(
        FoV,
        4.0 / 3.0,
        0.1,
        100.0
    )
    
    ViewMatrix = pyrr.Matrix44.look_at(
        position, 
        position + direction,
        up
    )

    last_time = currentTime

def intrinsic2projection(K):

    W = 1920.0
    H = 1080.0
    N = 0.1
    F = 1000.0
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
    return pyrr.Matrix44(np.array([
        [P_00, 0.0, P_02, 0.0],
        [0.0, P_11, P_12, 0.0],
        [0.0, 0.0, P_22, P_23],
        [0.0, 0.0, P_32, P_33]
    ], dtype=np.float32))

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

    view_matrix_pyrr = pyrr.Matrix44(M_np)
    
    return view_matrix_pyrr

ViewMatrix = pyrr.Matrix44.identity()
ProjectionMatrix = pyrr.Matrix44.identity()

#                  [ 0.0174309153850209],
#                  [-1.5293934899201675]], dtype=np.float64),
#                  np.array([[-12.85827522319373],
#                  [  5.354023300528274],
#                  [ 31.52413626328821]], dtype=np.float64))

#     [1384.4075990238498, 0.0, 965.373576378124],
#     [0.0, 1411.198765052427, 566.9750634841033],
#     [0.0, 0.0, 1.0]
position = pyrr.Vector3([0.0, 0.0, 5.0])
horizontalAngle = math.pi
verticalAngle = 0.0
initialFoV = 45.0

speed = 3.0
mouseSpeed = 0.005

last_time = 0.0


#     [ 1.4420912,   0.,         -0.00559747,  0.        ],
#  [ 0.,          2.613331,    0.04995382,  0.        ],
#  [ 0.,          0.,         -1.002002,   -0.2002002 ],
#  [ 0.,          0.,         -1.,          0.        ]]

#  [  0.9402884,    0.05947537,  -0.3351423,   -5.3540235 ],
#  [ -0.33361143,   0.35639465,  -0.8727464,  -31.524136  ],
#  [  0.,           0.,           0.,           1.        ]]
