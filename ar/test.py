#!/usr/bin/env python3
"""
AR with modern OpenGL core profile (shaders, VAO/VBO).
- Background: camera frame as a textured full-screen quad.
- Cube: drawn using VBO/IBO with per-vertex color, transformed by MVP (proj * modelview).
"""
import camera
import sys
import ctypes
import numpy as np
import cv2
import glfw
from OpenGL.GL import *
CAMERA_INDEX = 1
CAMERA_CALIB_FILE = "camera_calib.npz"
PATTERN_SIZE = (6, 9)
SQUARE_SIZE_M = 0.01
NEAR = 0.01
FAR = 100.0
WINDOW_NAME = "AR OpenGL Core (press ESC to quit)"

def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    status = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not status:
        log = glGetShaderInfoLog(shader).decode()
        glDeleteShader(shader)
        raise RuntimeError(f"Shader compile error ({shader_type}):\n{log}")
    return shader
def link_program(vs_src, fs_src):
    vs = compile_shader(vs_src, GL_VERTEX_SHADER)
    fs = compile_shader(fs_src, GL_FRAGMENT_SHADER)
    prog = glCreateProgram()
    glAttachShader(prog, vs)
    glAttachShader(prog, fs)
    glLinkProgram(prog)
    status = glGetProgramiv(prog, GL_LINK_STATUS)
    if not status:
        log = glGetProgramInfoLog(prog).decode()
        glDeleteProgram(prog)
        glDeleteShader(vs)
        glDeleteShader(fs)
        raise RuntimeError(f"Program link error:\n{log}")

    glDetachShader(prog, vs)
    glDetachShader(prog, fs)
    glDeleteShader(vs)
    glDeleteShader(fs)
    return prog

VS_BG = """
#version 330 core
layout(location = 0) in vec2 aPos;    // clip-space quad positions
layout(location = 1) in vec2 aTex;    // texcoords
out vec2 vTex;
void main() {
    vTex = aTex;
    gl_Position = vec4(aPos, 0.0, 1.0);
}
"""

FS_BG = """
#version 330 core
in vec2 vTex;
out vec4 FragColor;
uniform sampler2D uTex;
void main() {
    FragColor = texture(uTex, vTex);
}
"""

VS_3D = """
#version 330 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aColor;
uniform mat4 uMVP;
out vec3 vColor;
void main() {
    vColor = aColor;
    gl_Position = uMVP * vec4(aPos, 1.0);
}
"""

FS_3D = """
#version 330 core
in vec3 vColor;
out vec4 FragColor;
void main() {
    FragColor = vec4(vColor, 1.0);
}
"""
def make_object_points(pattern_size, square_size):
    cols, rows = pattern_size
    objp = np.zeros((cols * rows, 3), np.float32)
    objp[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)
    objp *= square_size
    return objp
def build_projection_matrix(camera_matrix, image_size, near, far):

    fx = camera_matrix[0, 0]
    fy = camera_matrix[1, 1]
    cx = camera_matrix[0, 2]
    cy = camera_matrix[1, 2]
    w, h = image_size
    left = -cx * near / fx
    right = (w - cx) * near / fx
    top = cy * near / fy
    bottom = -(h - cy) * near / fy

    proj = np.zeros((4, 4), dtype=np.float32)
    proj[0, 0] = 2 * near / (right - left)
    proj[0, 2] = (right + left) / (right - left)
    proj[1, 1] = 2 * near / (top - bottom)
    proj[1, 2] = (top + bottom) / (top - bottom)
    proj[2, 2] = -(far + near) / (far - near)
    proj[2, 3] = -2 * far * near / (far - near)
    proj[3, 2] = -1.0
    return proj
def pose_model(rvec, tvec):

    R, _ = cv2.Rodrigues(rvec)
    M = np.eye(4, dtype=np.float32)
    M[:3, :3] = R
    M[:3, 3] = tvec.flatten()
    cv_to_gl = np.diag([1.0, -1.0, -1.0, 1.0]).astype(np.float32)
    MV = cv_to_gl @ M
    return MV

def create_texture(w, h):
    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB8, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
    glBindTexture(GL_TEXTURE_2D, 0)
    return tex
def update_texture(tex, frame_bgr):
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    frame_rgb = cv2.flip(frame_rgb, 0)
    h, w = frame_rgb.shape[:2]
    glBindTexture(GL_TEXTURE_2D, tex)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE, frame_rgb)
    glBindTexture(GL_TEXTURE_2D, 0)
def create_bg_vao():
    data = np.array([

        -1.0, -1.0, 0.0, 0.0,
         1.0, -1.0, 1.0, 0.0,
         1.0,  1.0, 1.0, 1.0,
        -1.0,  1.0, 0.0, 1.0,
    ], dtype=np.float32)

    indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    ebo = glGenBuffers(1)

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(0))

    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(2 * 4))

    glBindVertexArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
    return vao, vbo, ebo, indices.size
def create_cube_vao(size=0.01):
    a = float(size)
    verts = np.array([

        0.0,  0.0,  0.0,   0.0, 1.0, 0.0,
        a,    0.0,  0.0,   0.0, 0.0, 1.0,
        a,    a,    0.0,   1.0, 1.0, 0.0,
        0.0,  a,    0.0,   1.0, 0.0, 1.0,
        0.0,  0.0, -a,     0.7, 0.7, 0.7,
        a,    0.0, -a,     0.7, 0.7, 0.7,
        a,    a,   -a,     0.7, 0.7, 0.7,
        0.0,  a,   -a,     0.7, 0.7, 0.7,
    ], dtype=np.float32)
    indices = np.array([

        0, 1, 2, 2, 3, 0,

        4, 5, 6, 6, 7, 4,

        0, 4, 7, 7, 3, 0,

        1, 5, 6, 6, 2, 1,

        0, 1, 5, 5, 4, 0,

        3, 2, 6, 6, 7, 3,
    ], dtype=np.uint32)

    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    ebo = glGenBuffers(1)

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    stride = (3 + 3) * 4

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))

    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))

    glBindVertexArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
    return vao, vbo, ebo, indices.size

def main():
    camera_matrix = camera.CAMERA_MATRIX
    dist_coeffs = camera.DIST_COEFFS

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("Cannot open camera index", CAMERA_INDEX)
        sys.exit(1)
    ret, frame = cap.read()
    if not ret:
        print("Failed to read from camera")
        sys.exit(1)
    h, w = frame.shape[:2]
    if not glfw.init():
        print("glfw.init failed")
        sys.exit(1)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.RESIZABLE, False)

    window = glfw.create_window(w, h, WINDOW_NAME, None, None)
    if not window:
        glfw.terminate()
        print("Failed to create window")
        sys.exit(1)

    glfw.make_context_current(window)
    glViewport(0, 0, w, h)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    prog_bg = link_program(VS_BG, FS_BG)
    prog_3d = link_program(VS_3D, FS_3D)
    tex = create_texture(w, h)
    update_texture(tex, frame)

    vao_bg, vbo_bg, ebo_bg, bg_idx_count = create_bg_vao()
    vao_cube, vbo_cube, ebo_cube, cube_idx_count = create_cube_vao(size=0.01)
    glUseProgram(prog_bg)
    loc_bg_tex = glGetUniformLocation(prog_bg, "uTex")
    glUniform1i(loc_bg_tex, 0)

    glUseProgram(prog_3d)
    loc_mvp = glGetUniformLocation(prog_3d, "uMVP")
    proj = build_projection_matrix(camera_matrix, (w, h), NEAR, FAR)

    objp = make_object_points(PATTERN_SIZE, SQUARE_SIZE_M)

    print("Starting AR (OpenGL core). Press ESC to exit. Move chessboard in front of camera.")
    while not glfw.window_should_close(window):
        ret, frame = cap.read()
        if not ret:
            print("Camera read failed")
            break
        ok, rvec, tvec = camera.detect_extrinsics(frame, objp)
        if not ok:
                rvec = None
                tvec = None

        update_texture(tex, frame)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(prog_bg)
        glDisable(GL_DEPTH_TEST)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, tex)
        glBindVertexArray(vao_bg)
        glDrawElements(GL_TRIANGLES, bg_idx_count, GL_UNSIGNED_INT, ctypes.c_void_p(0))
        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)
        glEnable(GL_DEPTH_TEST)
        glUseProgram(prog_3d)

        if rvec is not None and tvec is not None:
            MV = pose_model(rvec, tvec)

            MVP = proj @ MV
            glUniformMatrix4fv(loc_mvp, 1, GL_FALSE, (MVP.T).astype(np.float32))

            glBindVertexArray(vao_cube)
            glDrawElements(GL_TRIANGLES, cube_idx_count, GL_UNSIGNED_INT, ctypes.c_void_p(0))
            glBindVertexArray(0)

        glfw.swap_buffers(window)
        glfw.poll_events()

        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            break
    cap.release()
    glDeleteTextures([tex])
    glDeleteProgram(prog_bg)
    glDeleteProgram(prog_3d)
    glDeleteVertexArrays(1, [vao_bg])
    glDeleteBuffers(1, [vbo_bg])
    glDeleteVertexArrays(1, [vao_cube])
    glDeleteBuffers(1, [vbo_cube])
    glfw.terminate()
if __name__ == "__main__":
    main()
