import pypboy
import pygame
import game
import settings


class Module(pypboy.SubModule):

    label = "GENERAL"

    def __init__(self, *args, **kwargs):
        super(Module, self).__init__(*args, **kwargs)

