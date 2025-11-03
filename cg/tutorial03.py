import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glm
import numpy as np
import os
import sys
from common.shader import *


def main():

    if not glfw.init():
        print("Failed to initialize GLFW", file=sys.stderr)
        sys.exit(1)
    glfw.window_hint(glfw.SAMPLES, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    WIDTH, HEIGHT = 1024, 768
    window = glfw.create_window(WIDTH, HEIGHT, "Tutorial 03 - Matrices (Python)", None, None)
    
    if not window:
        print("Failed to open GLFW window.", file=sys.stderr)
        glfw.terminate()
        sys.exit(1)

    glfw.make_context_current(window)
    print("OpenGL context initialized.")
    glfw.set_input_mode(window, glfw.STICKY_KEYS, GL_TRUE)
    glClearColor(0.0, 0.0, 0.4, 0.0)


    VertexArrayID = glGenVertexArrays(1)
    glBindVertexArray(VertexArrayID)

    vertShader = read_shader_file('resource/shaders/matrix4.vert')
    fragShader = read_shader_file('resource/shaders/red_triangle.frag')


    programID = load_shaders(vertShader, fragShader)
    MatrixID = glGetUniformLocation(programID, "MVP")
    
    if MatrixID == -1:
        print("Warning: Could not find uniform 'MVP' in shader program.")

    Projection = glm.perspective(glm.radians(45.0), WIDTH / HEIGHT, 0.1, 100.0)

    View = glm.lookAt(
        glm.vec3(4, 3, 3),
        glm.vec3(0, 0, 0),
        glm.vec3(0, 1, 0)
    )

    Model = glm.mat4(1.0)
    MVP = Projection * View * Model

    g_vertex_buffer_data = np.array([
        -1.0, -1.0, 0.0,
         1.0, -1.0, 0.0,
         0.0,  1.0, 0.0,
    ], dtype=np.float32)
    vertexbuffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer)

    glBufferData(GL_ARRAY_BUFFER, g_vertex_buffer_data.nbytes, g_vertex_buffer_data, GL_STATIC_DRAW)


    while (glfw.get_key(window, glfw.KEY_ESCAPE) != glfw.PRESS and 
           not glfw.window_should_close(window)):
        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(programID)

        glUniformMatrix4fv(MatrixID, 1, GL_FALSE, glm.value_ptr(MVP))
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


    print("\nCleaning up resources...")
    glDeleteBuffers(1, [vertexbuffer])
    glDeleteProgram(programID)
    glDeleteVertexArrays(1, [VertexArrayID])
    glfw.terminate()

if __name__ == "__main__":
    main()
