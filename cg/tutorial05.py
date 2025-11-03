import glfw
from OpenGL.GL import *
import glm
import numpy as np
import sys
from common import *

VERTEX_SHADER_SOURCE = read_shader_file('resource/shaders/textured_cube.vert')

FRAGMENT_SHADER_SOURCE = read_shader_file('resource/shaders/textured_cube.frag')

def main():
    if not glfw.init():
        sys.exit(1)

    WIDTH, HEIGHT = 1024, 768

    glfw.window_hint(glfw.SAMPLES, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(WIDTH, HEIGHT, "Tutorial 05 - Textured Cube", None, None)
    
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
        glm.vec3(4, 3, 3),
        glm.vec3(0, 0, 0),
        glm.vec3(0, 1, 0)
    )
    
    Model = glm.mat4(1.0)
    
    MVP = Projection * View * Model
    

    Texture = load_dds_texture('resource/textures/uvtemplate.DDS')
    
    TextureID = glGetUniformLocation(programID, "myTextureSampler")
    
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

    g_uv_buffer_data = np.array([
        0.000059, 1.0-0.000004, 0.000103, 1.0-0.336048, 0.335973, 1.0-0.335903, 
        1.000023, 1.0-0.000013, 0.667979, 1.0-0.335851, 0.999958, 1.0-0.336064, 
        0.667979, 1.0-0.335851, 0.336024, 1.0-0.671877, 0.667969, 1.0-0.671889, 
        1.000023, 1.0-0.000013, 0.668104, 1.0-0.000013, 0.667979, 1.0-0.335851, 
        0.000059, 1.0-0.000004, 0.335973, 1.0-0.335903, 0.336098, 1.0-0.000071, 
        0.667979, 1.0-0.335851, 0.335973, 1.0-0.335903, 0.336024, 1.0-0.671877, 
        1.000004, 1.0-0.671847, 0.999958, 1.0-0.336064, 0.667979, 1.0-0.335851, 
        0.668104, 1.0-0.000013, 0.335973, 1.0-0.335903, 0.667979, 1.0-0.335851, 
        0.335973, 1.0-0.335903, 0.668104, 1.0-0.000013, 0.336098, 1.0-0.000071, 
        0.000103, 1.0-0.336048, 0.000004, 1.0-0.671870, 0.336024, 1.0-0.671877, 
        0.000103, 1.0-0.336048, 0.336024, 1.0-0.671877, 0.335973, 1.0-0.335903, 
        0.667969, 1.0-0.671889, 1.000004, 1.0-0.671847, 0.667979, 1.0-0.335851
    ], dtype=np.float32)

    vertexbuffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer)
    glBufferData(GL_ARRAY_BUFFER, g_vertex_buffer_data.nbytes, g_vertex_buffer_data, GL_STATIC_DRAW)

    uvbuffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, uvbuffer)
    glBufferData(GL_ARRAY_BUFFER, g_uv_buffer_data.nbytes, g_uv_buffer_data, GL_STATIC_DRAW)

    while (glfw.get_key(window, glfw.KEY_ESCAPE) != glfw.PRESS and 
           not glfw.window_should_close(window)):

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(programID)

        glUniformMatrix4fv(MatrixID, 1, GL_FALSE, glm.value_ptr(MVP))

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, Texture)
        glUniform1i(TextureID, 0)

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
        glBindBuffer(GL_ARRAY_BUFFER, uvbuffer)
        glVertexAttribPointer(
            1,
            2,
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
    glDeleteBuffers(1, [uvbuffer])
    glDeleteProgram(programID)
    glDeleteTextures(1, [Texture])
    glDeleteVertexArrays(1, [VertexArrayID])

    glfw.terminate()

if __name__ == "__main__":
    main()
