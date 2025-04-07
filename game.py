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