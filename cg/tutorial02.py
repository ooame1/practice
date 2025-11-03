import glfw
from OpenGL.GL import *
import numpy as np
import sys
from common.shader import *


VERTEX_SHADER_SOURCE = read_shader_file('resource/shaders/red_triangle.vert')
FRAGMENT_SHADER_SOURCE = read_shader_file('resource/shaders/red_triangle.frag')

def main():

    if not glfw.init():
        print("Failed to initialize GLFW", file=sys.stderr)
        return -1
    glfw.window_hint(glfw.SAMPLES, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    window = glfw.create_window(1024, 768, "Tutorial 03 - Matrices (Python)", None, None)
    if not window:
        print("Failed to open GLFW window.", file=sys.stderr)
        glfw.terminate()
        return -1

    glfw.make_context_current(window)
    glfw.set_input_mode(window, glfw.STICKY_KEYS, GL_TRUE)
    glClearColor(0.0, 0.0, 0.4, 0.0)
    vertex_array_id = glGenVertexArrays(1)
    glBindVertexArray(vertex_array_id)
    program_id = load_shaders(VERTEX_SHADER_SOURCE, FRAGMENT_SHADER_SOURCE)
    if program_id == 0:
        glfw.terminate()
        return -1
    g_vertex_buffer_data = np.array([
        -1.0, -1.0, 0.0,
         1.0, -1.0, 0.0,
         0.0,  1.0, 0.0,
    ], dtype=np.float32)
    vertexbuffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer)

    glBufferData(GL_ARRAY_BUFFER, g_vertex_buffer_data.nbytes, g_vertex_buffer_data, GL_STATIC_DRAW)
    
    while (
        glfw.get_key(window, glfw.KEY_ESCAPE) != glfw.PRESS and 
        not glfw.window_should_close(window)
    ):
        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(program_id)
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer)
        glVertexAttribPointer(
            0,
            3,
            GL_FLOAT,
            GL_FALSE,
            0,
            None
        )
        glDrawArrays(GL_TRIANGLES, 0, 3)

        glDisableVertexAttribArray(0)
        glfw.swap_buffers(window)
        glfw.poll_events()

    glDeleteBuffers(1, [vertexbuffer])
    glDeleteProgram(program_id)
    glDeleteVertexArrays(1, [vertex_array_id])

    glfw.terminate()
    print("Application closed successfully.")
    return 0

if __name__ == "__main__":
    main()
