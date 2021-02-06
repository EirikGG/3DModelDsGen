import pyrender, trimesh, random, math

import numpy as np

def generate_random_scene(model):
    scene = pyrender.Scene()                                    # Create new scene

    scene, model_node = _add_model(scene, model)                # Add model to scene

    for l_type in ['directional_lights', 'point_lights']:       # Adds light to the scene
        scene = _add_lighting(scene, light_type=l_type)

    scene, cam = _add_camera(scene)                             # Add camera

    for axis in ['x', 'y', 'z']:                                # Adds rotation about all three axises
        scene = _add_rotation(                                  
            scene,  
            model_node,
            random.uniform(0, 2*math.pi),                       # Find random angle and convert to radians
            axis
        )

    pyrender.Viewer(scene)

    return scene, model_node, cam

def _add_model(scene, model, pose=np.eye(4)):
    '''Adds a model to the scene, default position is origin.
    Returns scene and models node.'''
    node = scene.add(model, pose=pose)
    return scene, node

def _add_lighting(scene, light_type, random_range=(1, 4)):
    '''Takes scene and adds random amout of lighting.
    random_range:   Range to pick number of lights from.'''
    n = random.randrange(                                       # Number of lights
        random_range[0],
        random_range[1]
    )                    

    for _ in range(n):                                          # Add directional lights
        d = None
        if 'directional_lights'==light_type:
            d = pyrender.DirectionalLight(color=[1.0,1.0,1.0], intensity=2.0)
        elif 'point_lights'==light_type:
            d = pyrender.PointLight(color=[1.0,1.0,1.0], intensity=2.0)
        else:
            raise Exception('Light type not recognized, should be \"direction_lights\" or \"point_lights\", not {}'.format(light_type))

        scene.add(d)

    return scene


def _add_camera(scene):
    '''Adds a camera to the scene'''
    cam = pyrender.PerspectiveCamera(                           # Create perspective camera
        yfov=np.pi/3.0
    )

    cam = scene.add(cam)                                        # Add camera to scene

    a_x = random.uniform(-.5, .5)                               # Random x angle
    a_y = random.uniform(-.5, .5)                               # Random y angle

    scene = _add_rotation(scene, cam, a_y, 'y')                 # Add rotation
    scene = _add_rotation(scene, cam, a_x, 'x')

    t_z = random.uniform(.5, 1.5)                               # Random translation

    scene = _add_translation(scene, cam, z=t_z)                 # Add translation

    return scene, cam

def _add_rotation(scene, model, angle, axis):
    '''Applies a rotation matrix to the model'''
    mat = np.eye(4)
    if 'x'==axis:
        mat = np.array([                                        # Rotation matrix for x axis
            [1, 0, 0, 0],
            [0, math.cos(angle), -math.sin(angle), 0],
            [0, math.sin(angle), math.cos(angle), 0],
            [0, 0, 0, 1]
        ])

    elif 'y'==axis:
        mat = np.array([                                        # Rotation matrix for y axis
            [math.cos(angle), 0, math.sin(angle), 0],
            [0, 1, 0, 0],
            [-math.sin(angle), 0, math.cos(angle), 0],
            [0, 0, 0, 1]
        ])

    elif 'z'==axis:
        mat = np.array([                                        # Rotation matrix for z axis
            [math.cos(angle), -math.sin(angle), 0, 0],
            [math.sin(angle), math.cos(angle), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1] 
        ])
    scene = _update_model(scene, model, mat)
    return scene


def _add_translation(scene, model, x=0, y=0, z=0):
    '''Applies a translation matrix to the model'''
    mat = np.array([                                            # Translation matrix
        [1, 0, 0, x],
        [0, 1, 0, y],
        [0, 0, 1, z],
        [0, 0, 0, 1]
    ])
    scene = _update_model(scene, model, mat)
    return scene

def _update_model(scene, model, mat):
    '''Transposes matrix and applies it to the  model.
    Using method to avoid transposing multiple places 
    in the script.'''
    old = scene.get_pose(model)
    scene.set_pose(model, pose=np.matmul(mat, old))
    return scene