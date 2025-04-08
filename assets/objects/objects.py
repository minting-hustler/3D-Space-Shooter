import numpy as np
import os

###############################################################
# Write logic to load OBJ Files:
    # Will depend on type of object. For example if normals needed along with vertex positions 
    # then will need to load slightly differently.

# Can use the provided OBJ files from assignment_2_template/assets/objects/models/
# Can also download other assets or model yourself in modelling softwares like blender

###############################################################
# Create Transporter, Pirates, Stars(optional), Minimap arrow, crosshair, planet, spacestation, laser


###############################################################

def create_sphere(radius, segments):
    vertices = []
    indices = []

    for y in range(segments + 1):
        for x in range(segments + 1):
            x_segment = x / segments
            y_segment = y / segments
            x_pos = radius * np.cos(x_segment * 2.0 * np.pi) * np.sin(y_segment * np.pi)
            y_pos = radius * np.cos(y_segment * np.pi)
            z_pos = radius * np.sin(x_segment * 2.0 * np.pi) * np.sin(y_segment * np.pi)

            vertices.extend([x_pos, y_pos, z_pos])

    for y in range(segments):
        for x in range(segments):
            i0 = y * (segments + 1) + x
            i1 = i0 + 1
            i2 = i0 + (segments + 1)
            i3 = i2 + 1

            indices.extend([i0, i2, i1])
            indices.extend([i1, i2, i3])

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

def get_sphere():
    vertices, indices = create_sphere(1, 32)
    sphere_properties = {
        'vertices': vertices,
        'indices': indices,
        'position': np.array([100, 0, 0], dtype=np.float32),
        'velocity': np.array([0, 0, 0], dtype=np.float32),
        'rotation': np.array([0, 0, 0], dtype=np.float32),
        'scale': np.array([1, 1, 1], dtype=np.float32),
        'color': np.array([1, 0, 0, 1], dtype=np.float32),
        'sens': 250,
    }

    return sphere_properties

def rotation_matrix(rx, ry, rz):
        cx, cy, cz = np.cos([rx, ry, rz])
        sx, sy, sz = np.sin([rx, ry, rz])
        
        Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
        Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
        Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
        
        return Rz @ Ry @ Rx

def load_obj(file_path, color=np.array([1, 1, 1]), rotation=np.array([0,0,0], dtype=np.float32)):
    vertex_map = {}
    vertices = []
    indices = []
    temp_vertices = []
    temp_normals = []
    R = rotation_matrix(*rotation)
    R_invT = np.linalg.inv(R).T

    with open(file_path, 'r') as f:
        for line in f:
            parts = line.split()
            if parts[0] == 'v':
                v = np.array(list(map(float, parts[1:4])))
                rotated_v = R @ v
                temp_vertices.append(rotated_v)
            elif parts[0] == 'vn':
                vn = np.array(list(map(float, parts[1:4])))
                rotated_vn = R_invT @ vn
                temp_normals.append(rotated_vn)
            elif parts[0] == 'f':
                face_vertices = []
                for part in parts[1:4]:
                    v_idx, vn_idx = map(int, part.split('//'))
                    v_idx -= 1
                    vn_idx -= 1
                    key = (v_idx, vn_idx)
                    if key not in vertex_map:
                        vertex_map[key] = len(vertices) // 9
                        vertices.extend([
                            *temp_vertices[v_idx],
                            *temp_normals[vn_idx],
                            *color
                        ])
                    face_vertices.append(vertex_map[key])
                indices.extend(face_vertices)

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)


def get_transporter():
    obj_file = 'assets/objects/models/transporter.obj'
    vertices, indices = load_obj(obj_file, rotation = np.array([np.pi/2, np.pi/2, 0]))

    # Define properties for the Object class
    transporter_properties = {
        "vertices": vertices,
        "indices": indices,
        "position": np.array([100, 100, 0], dtype=np.float32),
        "rotation": np.array([np.pi/2, np.pi/2, 0], dtype=np.float32),
        "scale": np.array([0.1, 0.1, 0.1], dtype=np.float32),
        "color": np.array([1, 1, 1, 1], dtype=np.float32),
        "speed": 4,
        "radius": 10,
    }

    return transporter_properties


def get_planet():
    obj_file = 'assets/objects/models/planet.obj'
    vertices, indices = load_obj(obj_file)

    # Define properties for the planet
    planet_properties = {
        "vertices": vertices.flatten().astype(np.float32),
        "indices": indices.flatten().astype(np.uint32),
        "position": np.array([0, 0, 0], dtype=np.float32),  # Updated in InitScene
        "rotation": np.array([0, 0, 0], dtype=np.float32),
        "scale": np.array([5, 5, 5], dtype=np.float32),  # Large planets
        "color": np.array([0.4, 0.6, 1.0, 1.0], dtype=np.float32),  # Blue-like planet
        "rotation_speed": 5  # Slow rotation
    }

    return planet_properties


def get_spacestation():
    obj_file = 'assets/objects/models/spacestation.obj'
    vertices, indices = load_obj(obj_file)

    # Define properties for the space station
    spacestation_properties = {
        "vertices": vertices.flatten().astype(np.float32),
        "indices": indices,
        "position": np.array([0, 0, 0], dtype=np.float32),  # Updated in InitScene
        "rotation": np.array([0, 0, 0], dtype=np.float32),
        "scale": np.array([1, 1, 1], dtype=np.float32),  # Smaller than planets
        "color": np.array([0.9, 0.9, 0.9, 1.0], dtype=np.float32),  # White/Grey stations
        "orbit_radius": 150,  # Default value (Updated in InitScene)
        "orbit_speed": 5,  # Faster orbit speed than planets
        "orbit_center": np.array([0, 0, 0], dtype=np.float32),  # Planet it orbits around
        "orbit_angle": np.random.uniform(0, 2*np.pi),
        "radius": 20,
        "is_destination": False
    }

    return spacestation_properties


def get_pirate():
    obj_file = 'assets/objects/models/pirate.obj'
    vertices, indices = load_obj(obj_file)

    # Define properties for the pirate ships
    pirate_properties = {
        "vertices": vertices.flatten().astype(np.float32),
        "indices": indices,
        "position": np.array([0, 0, 0], dtype=np.float32),  # Updated in InitScene
        "rotation": np.array([0, 0, 0], dtype=np.float32),
        "scale": np.array([0.3, 0.3, 0.3], dtype=np.float32),  # Smaller than transporter
        "color": np.array([0, 1, 0, 1], dtype=np.float32),  # Red pirate ships
        "speed": np.random.uniform(2, 5),  # Random movement speed
        "radius": 10
    }

    return pirate_properties