import imgui
import numpy as np
from utils.graphics import Object, Camera, Shader
from assets.shaders.shaders import object_shader
from assets.objects.objects import *
import sys
from utils.graphics import Object
import copy
from time import sleep

class Game:
    def __init__(self, height, width, gui):
        self.gui = gui
        self.height = height
        self.width = width
        self.screen = 0
        self.shaders = [Shader(object_shader["vertex_shader"], object_shader["fragment_shader"])]
        self.objects = {}
        self.first_person_mode = False
        self.won = False
        self.lasers = []
        self.pirates = []

    def InitScene(self):
        if self.screen == 1:

            def setCamera():
                self.camera = Camera(self.height, self.width)
                self.camera.position = np.array([0, 0, 1], dtype=np.float32)
                self.camera.lookAt = np.array([0, 0, -1], dtype=np.float32)
                self.camera.up = np.array([0, 1, 0], dtype=np.float32)
                self.camera.fov = 90
            setCamera()

            # Initialize transporter
            test_sphere = get_sphere()
            transporter_obj = get_transporter()
            test_sphere["position"] = [0, 0, -10]
            # self.objects["sphere"] = Object(None, self.shaders[0], test_sphere)
            self.objects["transporter"] = Object(None, self.shaders[0], transporter_obj)

            ############################################################################

            def setWorldLimits():
                self.worldMin = np.array([-5000, -5000, -5000], dtype=np.float32)
                self.worldMax = np.array([5000, 5000, 5000], dtype=np.float32)
            setWorldLimits()

            ############################################################################

            # Initialize Planets and space stations (Randomly place n planets and n spacestations within world bounds)
            self.n_planets = 30 # for example
            self.planets = []
            self.stations = []

            for i in range(self.n_planets):
                planet_position = np.array([
                    np.random.uniform(self.worldMin[0] + 4500, self.worldMax[0] - 4500),  # Leave space from edges
                    np.random.uniform(self.worldMin[1] + 4500, self.worldMax[1] - 4500),
                    np.random.uniform(self.worldMin[2] + 4500, self.worldMax[2] - 4500)
                ], dtype=np.float32)

                # Load planet model
                planet_obj = get_planet()
                planet_obj["position"] = planet_position
                planet_obj["scale"] = np.array([15, 15, 15], dtype=np.float32)  # Bigger than stations
                planet_obj["rotation_speed"] = np.random.uniform(0.01, 0.05)  # Slow rotation
                self.planets.append(planet_obj)

                # Load space station (Each planet gets one)
                orbit_radius = np.random.uniform(15, 25)
                orbit_angle = np.random.uniform(0, 2 * np.pi)
                orbit_speed = np.random.uniform(0.02, 0.1)  # Faster than planets

                station_obj = get_spacestation()
                station_obj["position"] = planet_position + np.array([
                    orbit_radius * np.cos(orbit_angle),
                    np.random.uniform(20, 30),  # Slight vertical offset
                    orbit_radius * np.sin(orbit_angle)
                ], dtype=np.float32)
                station_obj["orbit_radius"] = orbit_radius
                station_obj["orbit_speed"] = orbit_speed
                station_obj["orbit_center"] = planet_position

                self.stations.append(station_obj)

                # Add to objects dictionary
                self.objects[f"planet_{i}"] = Object(None, self.shaders[0], planet_obj)
                self.objects[f"station_{i}"] = Object(None, self.shaders[0], station_obj)

            ############################################################################

            # Initialize transporter: Start at a random planet
            start_planet_idx = np.random.randint(0, self.n_planets)
            target_station_idx = np.random.randint(0, self.n_planets)

            # Ensure start and target are different
            while target_station_idx == start_planet_idx:
                target_station_idx = np.random.randint(0, self.n_planets)

            self.transporter_start = self.planets[start_planet_idx]["position"]
            self.transporter_target = self.stations[target_station_idx]["position"]

            # Update transporter position
            self.objects["transporter"].position = self.transporter_start
            self.destination_index = np.random.randint(0, self.n_planets)
            self.objects[f"station_{self.destination_index}"].properties["color"] = np.array([1, 0, 0, 1.0], dtype=np.float32)
            self.objects[f"station_{self.destination_index}"].properties["is_destination"] = True
            ############################################################################

            # Initialize Pirates (Spawn at random locations within world bounds)
            self.n_pirates = 20
            self.objects["transporter"].properties["position"] = np.array([0, 0, 0], dtype=np.float32)
            for i in range(self.n_pirates):
                pirate_position = np.array([
                    np.random.uniform(self.worldMin[0]+4500, self.worldMax[0]-4500),
                    np.random.uniform(self.worldMin[1]+4500, self.worldMax[1]-4500),
                    np.random.uniform(self.objects["transporter"].properties["position"][2]-200, self.worldMax[2]-4500)
                ], dtype=np.float32)

                pirate_obj = get_pirate()
                pirate_obj["position"] = pirate_position
                pirate_obj["scale"] = np.array([1, 1, 3], dtype=np.float32)  # Smaller than transporter
                pirate_obj["speed"] = np.random.uniform(2, 5)  # Variable speeds
                pirate = Object(None, self.shaders[0], pirate_obj)
                self.pirates.append(pirate)

            # self.objects["crosshair"] = Object(None, self.shaders[0], get_crosshair())
            # self.objects["crosshair"].properties["position"] = copy.deepcopy(self.objects["transporter"].properties["position"]) + 10 * self.camera.lookAt
    
    def ProcessFrame(self, inputs, time):
        if self.screen == 0:
            self.DrawText()
            self.UpdateScene(inputs, time)
        if self.screen == 1:
            self.DrawText()
            self.UpdateScene(inputs, time)
            self.DrawScene()
        if self.screen == 2:
            self.DrawText()
            self.UpdateScene(inputs, time)
            self.DrawScene()
    
    def DrawText(self):
        pass

    def UpdateScene(self, inputs, time):
        dt = time['deltaTime']

        if self.screen == 1:
            transporter = self.objects["transporter"]

            if inputs["A"]:
                    transporter.properties['rotation'][1] = 0.8*dt  # Yaw left
            elif inputs["D"]:
                transporter.properties['rotation'][1] = -0.8*dt # Yaw right
            else:
                transporter.properties['rotation'][1] = 0
            
            if inputs["W"]:
                transporter.properties['rotation'][0] = 0.8*dt  # Pitch down
            elif inputs["S"]:
                transporter.properties['rotation'][0] = -0.8*dt  # Pitch up
            else:
                transporter.properties['rotation'][0] = 0
            
            if inputs["Q"]:
                transporter.properties['rotation'][2] = 0.8*dt  # Roll left
            elif inputs["E"]:
                transporter.properties['rotation'][2] = -0.8*dt # Roll right
            else:
                transporter.properties['rotation'][2] = 0

            if inputs["SPACE"]:  
                    self.objects["transporter"].properties["speed"] += 0.05
                    self.objects["transporter"].properties["speed"] = min(self.objects["transporter"].properties["speed"], 20)
            else:
                self.objects["transporter"].properties["speed"] = 0