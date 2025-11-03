import cv2
import glm
import numpy as np
import camera
import glfw
from OpenGL.GL import *
import points
from common import *

target_image_path = 'resource/target_frame.jpg'

VERTEX_SHADER_SOURCE = read_shader_file('resource/shaders/textured_cube.vert')

FRAGMENT_SHADER_SOURCE = read_shader_file('resource/shaders/textured_cube.frag')

def init(width, height):
    global window

    if not glfw.init():
        return None

    glfw.window_hint(glfw.SAMPLES, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(width, height, "AR Window", None, None)
    if not window:
        print("Failed to open GLFW window.")
        glfw.terminate()
        return

    glfw.make_context_current(window)

    glfw.set_input_mode(window, glfw.STICKY_KEYS, GL_TRUE)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    
    glfw.poll_events()
    glfw.set_cursor_pos(window, width / 2, height / 2)

    glClearColor(0.0, 0.0, 0.4, 0.0)

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glEnable(GL_CULL_FACE)
    glEnable(GL_PROGRAM_POINT_SIZE)

def load_background(width, height):
    global bgVertexbuffer, bgUvbuffer, bgProgramID, bgMatrixID, bgTextureID, bgVertexArrayID

    bgVertexArrayID = glGenVertexArrays(1)
    glBindVertexArray(bgVertexArrayID)

    bgProgramID = load_shaders(VERTEX_SHADER_SOURCE, FRAGMENT_SHADER_SOURCE)
    bgMatrixID = glGetUniformLocation(bgProgramID, "MVP")
    bgTextureID = glGetUniformLocation(bgProgramID, "myTextureSampler")

    vertices = np.array([
        0,  height, 0.0,
        0, 0, 0.0,
        width,  height, 0.0,
        width,  height, 0.0,
        0, 0, 0.0,
        width, 0, 0.0,
    ], dtype=np.float32)

    uvs = np.array([
        0.0, 1.0,
        0.0, 0.0,
        1.0, 1.0,
        1.0, 1.0,
        0.0, 0.0,
        1.0, 0.0,
    ], dtype=np.float32)

    bgVertexbuffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, bgVertexbuffer)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    bgUvbuffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, bgUvbuffer)
    glBufferData(GL_ARRAY_BUFFER, uvs.nbytes, uvs, GL_STATIC_DRAW)

def load_texture_from_frame(frame):
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    frame = cv2.flip(frame, 0)
    frame_data = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, frame.shape[1], frame.shape[0], 0,
                 GL_RGB, GL_UNSIGNED_BYTE, frame_data)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture_id

def draw_background(frame):

    glBindVertexArray(bgVertexArrayID)
    glUseProgram(bgProgramID)

    proj = glm.ortho(0, frame.shape[1], 0, frame.shape[0], -1.0, 1.0)
    glUniformMatrix4fv(bgMatrixID, 1, GL_FALSE, glm.value_ptr(proj))
    texture_id = load_texture_from_frame(frame)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glUniform1i(bgTextureID, 0)

    glEnableVertexAttribArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, bgVertexbuffer)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

    glEnableVertexAttribArray(1)
    glBindBuffer(GL_ARRAY_BUFFER, bgUvbuffer)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)

    glDrawArrays(GL_TRIANGLES, 0, 6)
def load_objects():
    global objVertexbuffer, objUvbuffer, objProgramID, objMatrixID, objTextureID, objVertexArrayID, objTexture, objVertices

    objVertexArrayID = glGenVertexArrays(1)
    glBindVertexArray(objVertexArrayID)

    objProgramID = load_shaders(VERTEX_SHADER_SOURCE, FRAGMENT_SHADER_SOURCE)

    objMatrixID = glGetUniformLocation(objProgramID, "MVP")
    objTextureID = glGetUniformLocation(objProgramID, "myTextureSampler")

    objTexture = load_dds_texture("resource/textures/uvmap.DDS")

    success, vertices_list, uvs_list, normals_list = load_obj("resource/models/cube.obj")

    if not success:
        print(f"Failed to load model.")
        glfw.terminate()
        return

    objVertices = np.array(vertices_list, dtype=np.float32)
    objUvs = np.array(uvs_list, dtype=np.float32)

    objVertexbuffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, objVertexbuffer)
    glBufferData(GL_ARRAY_BUFFER, objVertices.nbytes, objVertices, GL_STATIC_DRAW)

    objUvbuffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, objUvbuffer)
    glBufferData(GL_ARRAY_BUFFER, objUvs.nbytes, objUvs, GL_STATIC_DRAW)

def compute_matrices_from_frame(rvec, tvec):
    Projection = camera.Projection
    View = camera.extrinsic2ViewMatrix(rvec, tvec)
    Model = np.array([[1, 0, 0, 0],
                      [0, 1, 0, 1],
                      [0, 0, 1, -1],
                      [0, 0, 0, 2]], dtype=np.float32)

    mvp = Projection @ View @ Model
    glUniformMatrix4fv(objMatrixID, 1, GL_FALSE, (mvp.T).astype(np.float32))

def draw_objects(rvec, tvec):
    glBindVertexArray(objVertexArrayID)
    glUseProgram(objProgramID)
    compute_matrices_from_frame(rvec, tvec)

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, objTexture)
    glUniform1i(objTextureID, 0)

    glEnableVertexAttribArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, objVertexbuffer)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

    glEnableVertexAttribArray(1)
    glBindBuffer(GL_ARRAY_BUFFER, objUvbuffer)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)
    glDrawArrays(GL_TRIANGLES, 0, len(objVertices))

def main():
    cap = cv2.VideoCapture(camera.CAMERA_DEVICE_INDEX)
    ret, frame = cap.read()
    height, width = frame.shape[:2]
    init(width // 2, height // 2)
    load_background(width, height)
    load_objects()
    points.load()

    while (
        glfw.get_key(window, glfw.KEY_ESCAPE) != glfw.PRESS and 
        not glfw.window_should_close(window)
    ):
        ret, frame = cap.read()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)
        draw_background(frame)

        ret, rvec, tvec = camera.detect_extrinsics(frame)
        if ret:
            points.draw(rvec, tvec)
            draw_objects(rvec, tvec)
        glfw.swap_buffers(window)
        glfw.poll_events()
        if cv2.waitKey(30) == ord('q'):
            break

if __name__ == "__main__":
    main()
