import struct
import sys
from OpenGL.GL import *
import numpy as np
import struct

FOURCC_DXT1 = 0x31545844
FOURCC_DXT3 = 0x33545844
FOURCC_DXT5 = 0x35545844

GL_COMPRESSED_RGBA_S3TC_DXT1_EXT = 0x83F1
GL_COMPRESSED_RGBA_S3TC_DXT3_EXT = 0x83F2
GL_COMPRESSED_RGBA_S3TC_DXT5_EXT = 0x83F3

def load_bmp_texture(imagepath: str) -> GLuint:
    
    try:

        with open(imagepath, "rb") as file:
            

            header = file.read(54)

            if len(header) != 54:
                print("Not a correct BMP file (Header too short)")
                return 0

            if header[0:2].decode('ascii') != 'BM':
                print("Not a correct BMP file (Magic bytes missing)")
                return 0
            
            bits_per_pixel = struct.unpack('<H', header[0x1C:0x1C+2])[0]
            compression = struct.unpack('<I', header[0x1E:0x1E+4])[0]

            if compression != 0 or bits_per_pixel != 24:
                print("Not a correct BMP file (Must be uncompressed 24bpp)")
                return 0
            dataPos = struct.unpack('<I', header[0x0A:0x0A+4])[0]
            imageSize = struct.unpack('<I', header[0x22:0x22+4])[0]
            width = struct.unpack('<I', header[0x12:0x12+4])[0]
            height = struct.unpack('<I', header[0x16:0x16+4])[0]

            if imageSize == 0:
                imageSize = width * height * 3
            if dataPos == 0:
                dataPos = 54
            file.seek(dataPos)
            data = file.read(imageSize)
            
    except FileNotFoundError:
        print(f"{imagepath} could not be opened. Are you in the right directory ?")
        return 0
    except Exception as e:
        print(f"Error processing BMP file {imagepath}: {e}")
        return 0

    if len(data) != imageSize:
        print("Error: Read size does not match expected image size.")
        return 0
    textureID = glGenTextures(1)
    
    glBindTexture(GL_TEXTURE_2D, textureID)

    data_buffer = np.frombuffer(data, dtype=np.uint8)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_BGR, GL_UNSIGNED_BYTE, data_buffer)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    
    glGenerateMipmap(GL_TEXTURE_2D)

    glBindTexture(GL_TEXTURE_2D, 0)
    return textureID

def load_dds_texture(imagepath: str) -> GLuint:
    with open(imagepath, "rb") as f:
        header = f.read(128)
        if header[0:4] != b'DDS ':
            raise ValueError("Not a valid DDS file")

        height = struct.unpack_from("<I", header, 12)[0]
        width = struct.unpack_from("<I", header, 16)[0]
        mipmap_count = struct.unpack_from("<I", header, 28)[0]
        fourcc = header[84:88].decode('ascii')
        if fourcc == "DXT1":
            block_size = 8
            gl_format = GL_COMPRESSED_RGBA_S3TC_DXT1_EXT
        elif fourcc == "DXT3":
            block_size = 16
            gl_format = GL_COMPRESSED_RGBA_S3TC_DXT3_EXT
        elif fourcc == "DXT5":
            block_size = 16
            gl_format = GL_COMPRESSED_RGBA_S3TC_DXT5_EXT
        else:
            raise ValueError("Unsupported DDS format: " + fourcc)
        mipmaps = []
        w, h = width, height
        for level in range(max(1, mipmap_count)):
            size = ((w + 3) // 4) * ((h + 3) // 4) * block_size
            data = f.read(size)
            mipmaps.append({'width': w, 'height': h, 'size': size, 'data': data})
            w = max(1, w // 2)
            h = max(1, h // 2)
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)

    for level, mip in enumerate(mipmaps):
        glCompressedTexImage2D(
            GL_TEXTURE_2D,
            level,
            gl_format,
            mip['width'],
            mip['height'],
            0,
            mip['data']
        )
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    glBindTexture(GL_TEXTURE_2D, 0)
    return tex_id
