import glfw
from OpenGL.GL import *
import numpy as np
import sys

def main():
    if not glfw.init():
        sys.stderr.write("Failed to initialize GLFW\n")
        return -1

    glfw.window_hint(glfw.SAMPLES, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(1024, 768, "Tutorial 01 - Window (Python)", None, None)

    if not window:
        sys.stderr.write("Failed to open GLFW window. Check if your GPU supports OpenGL 3.3.\n")
        glfw.terminate()
        return -1

    glfw.make_context_current(window)

    glfw.set_input_mode(window, glfw.STICKY_KEYS, GL_TRUE)

    glClearColor(0.0, 0.0, 0.4, 0.0)

    while (glfw.get_key(window, glfw.KEY_ESCAPE) != glfw.PRESS and
           not glfw.window_should_close(window)):

        glClear(GL_COLOR_BUFFER_BIT)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()
    return 0

if __name__ == "__main__":
    main()