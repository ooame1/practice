import cv2
import glfw
from OpenGL.GL import *
import glm
import numpy as np
import sys
from common import *
import pyrr
import time
from common import *

VERTEX_SHADER_SOURCE = read_shader_file('resource/shaders/textured_cube.vert')

FRAGMENT_SHADER_SOURCE = read_shader_file('resource/shaders/textured_cube.frag')
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

position = pyrr.Vector3([0.0, 0.0, 3.0])

horizontalAngle = 3.14

verticalAngle = 0.0

initialFoV = 45.0

speed = 3.0

mouseSpeed = 0.005
lastTime = time.time()

def init():
    global window
    if not glfw.init():
        print("Failed to initialize GLFW")
        return

    glfw.window_hint(glfw.SAMPLES, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Python OpenGL Cube", None, None)
    if not window:
        print("Failed to open GLFW window.")
        glfw.terminate()
        return

    glfw.make_context_current(window)
    

    glfw.set_input_mode(window, glfw.STICKY_KEYS, GL_TRUE)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    

    glfw.poll_events()
    glfw.set_cursor_pos(window, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    glClearColor(0.0, 0.0, 0.4, 0.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glEnable(GL_CULL_FACE)

def load():
    global programID, MatrixID, TextureID, Texture, vertexbuffer, uvbuffer, VertexArrayID

    VertexArrayID = glGenVertexArrays(1)
    glBindVertexArray(VertexArrayID)
    programID = load_shaders(VERTEX_SHADER_SOURCE, FRAGMENT_SHADER_SOURCE)
    MatrixID = glGetUniformLocation(programID, "MVP")
    TextureID = glGetUniformLocation(programID, "myTextureSampler")
    

    Texture = load_dds_texture('resource/textures/uvtemplate.DDS')

    g_vertex_buffer_data = np.array([
		-1.0,-1.0,-1.0,
		-1.0,-1.0, 1.0,
		-1.0, 1.0, 1.0,
		 1.0, 1.0,-1.0,
		-1.0,-1.0,-1.0,
		-1.0, 1.0,-1.0,
		 1.0,-1.0, 1.0,
		-1.0,-1.0,-1.0,
		 1.0,-1.0,-1.0,
		 1.0, 1.0,-1.0,
		 1.0,-1.0,-1.0,
		-1.0,-1.0,-1.0,
		-1.0,-1.0,-1.0,
		-1.0, 1.0, 1.0,
		-1.0, 1.0,-1.0,
		 1.0,-1.0, 1.0,
		-1.0,-1.0, 1.0,
		-1.0,-1.0,-1.0,
		-1.0, 1.0, 1.0,
		-1.0,-1.0, 1.0,
		 1.0,-1.0, 1.0,
		 1.0, 1.0, 1.0,
		 1.0,-1.0,-1.0,
		 1.0, 1.0,-1.0,
		 1.0,-1.0,-1.0,
		 1.0, 1.0, 1.0,
		 1.0,-1.0, 1.0,
		 1.0, 1.0, 1.0,
		 1.0, 1.0,-1.0,
		-1.0, 1.0,-1.0,
		 1.0, 1.0, 1.0,
		-1.0, 1.0,-1.0,
		-1.0, 1.0, 1.0,
		 1.0, 1.0, 1.0,
		-1.0, 1.0, 1.0,
		 1.0,-1.0, 1.0
	], dtype=np.float32)

    g_uv_buffer_data = np.array([
		0.000059, 0.000004,
		0.000103, 0.336048,
		0.335973, 0.335903,
		1.000023, 0.000013,
		0.667979, 0.335851,
		0.999958, 0.336064,
		0.667979, 0.335851,
		0.336024, 0.671877,
		0.667969, 0.671889,
		1.000023, 0.000013,
		0.668104, 0.000013,
		0.667979, 0.335851,
		0.000059, 0.000004,
		0.335973, 0.335903,
		0.336098, 0.000071,
		0.667979, 0.335851,
		0.335973, 0.335903,
		0.336024, 0.671877,
		1.000004, 0.671847,
		0.999958, 0.336064,
		0.667979, 0.335851,
		0.668104, 0.000013,
		0.335973, 0.335903,
		0.667979, 0.335851,
		0.335973, 0.335903,
		0.668104, 0.000013,
		0.336098, 0.000071,
		0.000103, 0.336048,
		0.000004, 0.671870,
		0.336024, 0.671877,
		0.000103, 0.336048,
		0.336024, 0.671877,
		0.335973, 0.335903,
		0.667969, 0.671889,
		1.000004, 0.671847,
		0.667979, 0.335851
	], dtype=np.float32)
    vertexbuffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer)
    glBufferData(GL_ARRAY_BUFFER, g_vertex_buffer_data.nbytes, g_vertex_buffer_data, GL_STATIC_DRAW)
    uvbuffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, uvbuffer)
    glBufferData(GL_ARRAY_BUFFER, g_uv_buffer_data.nbytes, g_uv_buffer_data, GL_STATIC_DRAW)

def draw():

        glUseProgram(programID)
        compute_matrices_from_inputs(window)
        Projection = get_projection_matrix()
        View = get_view_matrix()
        Model = pyrr.Matrix44.identity()
        

        MVP = Projection * View * Model
        
        glUniformMatrix4fv(MatrixID, 1, GL_FALSE, MVP)
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
        glDrawArrays(GL_TRIANGLES, 0, 12 * 3)
        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)

def main():
    init()
    load()
    while (
        glfw.get_key(window, glfw.KEY_ESCAPE) != glfw.PRESS and 
        not glfw.window_should_close(window)
    ):

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw()

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