from OpenGL.GL import *
import sys

def load_shaders(vertex_shader_source, fragment_shader_source):
    vertex_shader_id = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader_id, vertex_shader_source)
    glCompileShader(vertex_shader_id)
    
    if glGetShaderiv(vertex_shader_id, GL_COMPILE_STATUS) != GL_TRUE:
        sys.stderr.write("Vertex Shader Compilation Failed:\n")
        sys.stderr.write(glGetShaderInfoLog(vertex_shader_id).decode() + "\n")
        glDeleteShader(vertex_shader_id)
        return 0
    fragment_shader_id = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader_id, fragment_shader_source)
    glCompileShader(fragment_shader_id)

    if glGetShaderiv(fragment_shader_id, GL_COMPILE_STATUS) != GL_TRUE:
        sys.stderr.write("Fragment Shader Compilation Failed:\n")
        sys.stderr.write(glGetShaderInfoLog(fragment_shader_id).decode() + "\n")
        glDeleteShader(vertex_shader_id)
        glDeleteShader(fragment_shader_id)
        return 0
    program_id = glCreateProgram()
    glAttachShader(program_id, vertex_shader_id)
    glAttachShader(program_id, fragment_shader_id)
    glLinkProgram(program_id)

    if glGetProgramiv(program_id, GL_LINK_STATUS) != GL_TRUE:
        sys.stderr.write("Shader Program Linking Failed:\n")
        sys.stderr.write(glGetProgramInfoLog(program_id).decode() + "\n")
        glDeleteProgram(program_id)
        return 0
    glDetachShader(program_id, vertex_shader_id)
    glDetachShader(program_id, fragment_shader_id)
    glDeleteShader(vertex_shader_id)
    glDeleteShader(fragment_shader_id)

    return program_id

def read_shader_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()