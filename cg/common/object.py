import pyrr

def load_obj(path):
    temp_vertices = []
    temp_uvs = []
    temp_normals = []

    vertex_indices = []
    uv_indices = []
    normal_indices = []

    try:
        with open(path, 'r') as file:
            for line in file:
                if not line.strip():
                    continue

                parts = line.split()
                if not parts:
                    continue

                line_header = parts[0]

                if line_header == 'v':
                    v = pyrr.Vector3([float(parts[1]), float(parts[2]), float(parts[3])])
                    temp_vertices.append(v)
                elif line_header == 'vt':

                    uv = [float(parts[1]), float(parts[2])]
                    uv[1] = -uv[1]
                    temp_uvs.append(uv)
                elif line_header == 'vn':
                    n = pyrr.Vector3([float(parts[1]), float(parts[2]), float(parts[3])])
                    temp_normals.append(n)
                elif line_header == 'f':
                    if len(parts) < 4:
                        return False, [], [], []

                    for i in range(1, 4):
                        indices = parts[i].split('/')
                        if len(indices) != 3:
                            return False, [], [], []

                        vertex_indices.append(int(indices[0]))
                        uv_indices.append(int(indices[1]))
                        normal_indices.append(int(indices[2]))
                else:
                    pass
    except FileNotFoundError:
        return False, [], [], []
    except Exception:
        return False, [], [], []

    out_vertices = []
    out_uvs = []
    out_normals = []

    for i in range(len(vertex_indices)):
        vertex_index = vertex_indices[i]
        uv_index = uv_indices[i]
        normal_index = normal_indices[i]

        vertex = temp_vertices[vertex_index - 1]
        uv = temp_uvs[uv_index - 1]
        normal = temp_normals[normal_index - 1]

        out_vertices.append(vertex)
        out_uvs.append(uv)
        out_normals.append(normal)

    return True, out_vertices, out_uvs, out_normals
