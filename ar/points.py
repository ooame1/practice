import numpy as np
import camera
import glfw
from OpenGL.GL import *
from common import *

vertices = camera.WORLD_POINTS.flatten().astype(np.float32)
Rvec = np.array([[-0.51213011], [-0.73448099], [-1.52129632]], dtype=np.float32)
Tvec = np.array([[-4.10532046], [1.37430213], [28.8477635]], dtype=np.float32)
VERTEX_SHADER_SOURCE = read_shader_file('resource/shaders/point.vert')
FRAGMENT_SHADER_SOURCE = read_shader_file('resource/shaders/point.frag')

def load():
    global programID, matrixID, vertexArrayID, vertexBuffer

    vertexArrayID = glGenVertexArrays(1)
    glBindVertexArray(vertexArrayID)

    vertexBuffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vertexBuffer)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    programID = load_shaders(VERTEX_SHADER_SOURCE, FRAGMENT_SHADER_SOURCE)
    matrixID = glGetUniformLocation(programID, "MVP")

def draw(rvec, tvec):
    glBindVertexArray(vertexArrayID)
    glUseProgram(programID)

    Projection = camera.Projection
    MV = camera.extrinsic2ViewMatrix(rvec, tvec)
    print(MV)
    MVP = Projection @ MV

    glUniformMatrix4fv(matrixID, 1, GL_FALSE, (MVP.T).astype(np.float32))

    glEnableVertexAttribArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, vertexBuffer)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

    glDrawArrays(GL_POINTS, 0, len(vertices))

    glDisableVertexAttribArray(0)

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

def main():
    init(1980 // 2, 1080 // 2)
    glDisable(GL_CULL_FACE)
    glDisable(GL_DEPTH_TEST)

    
    load()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        draw(Rvec, Tvec)
        glfw.swap_buffers(window)

    
    glDeleteBuffers(1, [vertexBuffer])
    glDeleteVertexArrays(1, [vertexArrayID])
    glDeleteProgram(programID)

    glfw.terminate()
if __name__ == "__main__":
    main()