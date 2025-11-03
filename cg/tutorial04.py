import glfw
from OpenGL.GL import *
import glm
import numpy as np
import sys
from common.shader import *
VERTEX_SHADER_SOURCE = read_shader_file('resource/shaders/colored_cube.vert')
FRAGMENT_SHADER_SOURCE = read_shader_file('resource/shaders/colored_cube.frag')

g_vertex_buffer_data = np.array([
        -1.0,-1.0,-1.0, -1.0,-1.0, 1.0, -1.0, 1.0, 1.0, 
         1.0, 1.0,-1.0, -1.0,-1.0,-1.0, -1.0, 1.0,-1.0, 
         1.0,-1.0, 1.0, -1.0,-1.0,-1.0,  1.0,-1.0,-1.0, 
         1.0, 1.0,-1.0,  1.0,-1.0,-1.0, -1.0,-1.0,-1.0, 
        -1.0,-1.0,-1.0, -1.0, 1.0, 1.0, -1.0, 1.0,-1.0, 
         1.0,-1.0, 1.0, -1.0,-1.0, 1.0, -1.0,-1.0,-1.0, 
        -1.0, 1.0, 1.0, -1.0,-1.0, 1.0,  1.0,-1.0, 1.0, 
         1.0, 1.0, 1.0,  1.0,-1.0,-1.0,  1.0, 1.0,-1.0, 
         1.0,-1.0,-1.0,  1.0, 1.0, 1.0,  1.0,-1.0, 1.0, 
         1.0, 1.0, 1.0,  1.0, 1.0,-1.0, -1.0, 1.0,-1.0, 
         1.0, 1.0, 1.0, -1.0, 1.0,-1.0, -1.0, 1.0, 1.0, 
         1.0, 1.0, 1.0, -1.0, 1.0, 1.0,  1.0,-1.0, 1.0
    ], dtype=np.float32)

g_color_buffer_data = np.array([
        0.583, 0.771, 0.014, 0.609, 0.115, 0.436, 0.327, 0.483, 0.844, 
        0.822, 0.569, 0.201, 0.435, 0.602, 0.223, 0.310, 0.747, 0.185, 
        0.597, 0.770, 0.761, 0.559, 0.436, 0.730, 0.359, 0.583, 0.152, 
        0.483, 0.596, 0.789, 0.559, 0.861, 0.639, 0.195, 0.548, 0.859, 
        0.014, 0.184, 0.576, 0.771, 0.328, 0.970, 0.406, 0.615, 0.116, 
        0.676, 0.977, 0.133, 0.971, 0.572, 0.833, 0.140, 0.616, 0.489, 
        0.997, 0.513, 0.064, 0.945, 0.719, 0.592, 0.543, 0.021, 0.978, 
        0.279, 0.317, 0.505, 0.167, 0.620, 0.077, 0.347, 0.857, 0.137, 
        0.055, 0.953, 0.042, 0.714, 0.505, 0.345, 0.783, 0.290, 0.734, 
        0.722, 0.645, 0.174, 0.302, 0.455, 0.848, 0.225, 0.587, 0.040, 
        0.517, 0.713, 0.338, 0.053, 0.959, 0.120, 0.393, 0.621, 0.362, 
        0.673, 0.211, 0.457, 0.820, 0.883, 0.371, 0.982, 0.099, 0.879
    ], dtype=np.float32)

def main():
    if not glfw.init():
        sys.exit(1)

    WIDTH, HEIGHT = 1024, 768

    glfw.window_hint(glfw.SAMPLES, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(WIDTH, HEIGHT, "Tutorial 04 - Colored Cube (Inline Shaders)", None, None)
    
    if not window:
        glfw.terminate()
        sys.exit(1)

    glfw.make_context_current(window)

    glfw.set_input_mode(window, glfw.STICKY_KEYS, GL_TRUE)

    glClearColor(0.0, 0.0, 0.4, 0.0)

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    VertexArrayID = glGenVertexArrays(1)
    glBindVertexArray(VertexArrayID)

    programID = load_shaders(VERTEX_SHADER_SOURCE, FRAGMENT_SHADER_SOURCE)

    MatrixID = glGetUniformLocation(programID, "MVP")

    Projection = glm.perspective(glm.radians(45.0), WIDTH / HEIGHT, 0.1, 100.0)
    
    View = glm.lookAt(
        glm.vec3(4, 3, -3),
        glm.vec3(0, 0, 0),
        glm.vec3(0, 1, 0)
    )
    
    Model = glm.mat4(1.0)
    
    MVP = Projection * View * Model

    vertexbuffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer)
    glBufferData(GL_ARRAY_BUFFER, g_vertex_buffer_data.nbytes, g_vertex_buffer_data, GL_STATIC_DRAW)

    colorbuffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, colorbuffer)
    glBufferData(GL_ARRAY_BUFFER, g_color_buffer_data.nbytes, g_color_buffer_data, GL_STATIC_DRAW)

    while (glfw.get_key(window, glfw.KEY_ESCAPE) != glfw.PRESS and 
           not glfw.window_should_close(window)):

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

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

        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, colorbuffer)
        glVertexAttribPointer(
            1,
            3,
            GL_FLOAT,
            GL_FALSE,
            0,
            None
        )

        glDrawArrays(GL_TRIANGLES, 0, 12*3)

        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        glfw.swap_buffers(window)

        glfw.poll_events()

    glDeleteBuffers(1, [vertexbuffer])
    glDeleteBuffers(1, [colorbuffer])
    glDeleteProgram(programID)
    glDeleteVertexArrays(1, [VertexArrayID])

    glfw.terminate()

if __name__ == "__main__":
    main()
