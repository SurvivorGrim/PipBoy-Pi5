# -*- coding: utf-8 -*-
import cairosvg
import pygame
import pypboy
import settings
import game
import io

# def load_svg(filename, width, height):
#     drawing = cairosvg.svg2png(url=filename)
#     byte_io = io.BytesIO(drawing)
#     image = pygame.image.load(byte_io).convert_alpha()
#     size = image.get_size()
#     scale = min(width / size[0], height / size[1])
#     if size[1] != height:
#         image = pygame.transform.smoothscale(image, (round(size[0] * scale), round(size[1] * scale)))
#     image.fill((0, 230, 0), None, pygame.BLEND_RGBA_MULT)
#     return image

class Module(pypboy.SubModule):
    label = ""
    zoom = settings.LOCAL_MAP_ZOOM
    map_top_edge = 30
    map_type = settings.MAP_TYPE
    map_width = 480
    map_height = 265
    map_rect = pygame.Rect(0, 0, 470, 500)

    def __init__(self, *args, **kwargs):
        super(Module, self).__init__(*args, **kwargs)
        # self.mapgrid = Map(self.map_width, self.map_height)

        if (settings.LOAD_CACHED_MAP):
            print("Loading cached map")
            self.mapgrid = Map(self.map_width, self.map_height, self.map_rect, "Loading cached map")
            self.mapgrid.load_map(settings.MAP_FOCUS, self.zoom, self.map_width, self.map_height, self.map_type)
        else:
            print("Loading map from local image")
            self.mapgrid = Map(self.map_width, self.map_height, self.map_rect, "Loading map from local image")
            self.mapgrid.load_local_map()

        self.add(self.mapgrid)
        self.mapgrid.rect[0] = 0
        self.mapgrid.rect[1] = self.map_top_edge

        self.topmenu = pypboy.ui.TopMenu()
        self.add(self.topmenu)
        self.topmenu.label = "MAP"
        self.topmenu.title = settings.MODULE_TEXT

        settings.FOOTER_TIME[2] = "Map Data © Google"
        self.footer = pypboy.ui.Footer(settings.FOOTER_TIME)
        self.footer.rect[0] = settings.footer_x
        self.footer.rect[1] = settings.footer_y
        self.add(self.footer)

    def handle_action(self, action, value=0):
        if action == "zoom_in":
            self.zoomMap(1)
        if action == "zoom_out":
            self.zoomMap(-1)

    # def handle_resume(self):
    #     super(Module, self).handle_resume()

    def zoomMap(self, zoomFactor):
        self.zoom = self.zoom + zoomFactor
        if settings.LOAD_CACHED_MAP:
            print("Loading cached map")
            self.mapgrid.load_map(settings.MAP_FOCUS, self.zoom, self.map_width, self.map_height, self.map_type)
        else:
            print("Loading map from local image")
            self.mapgrid.load_local_map()

        self.add(self.mapgrid)
        self.mapgrid.rect[0] = 0
        self.mapgrid.rect[1] = self.map_top_edge

class Map(game.Entity):
    _mapper = None
    _transposed = None
    _size = 0
    _fetching = None
    _map_surface = None
    _loading_size = 0
    _render_rect = None

    def __init__(self, width, height, render_rect=None, loading_type="Loading map...", *args, **kwargs):
        super(Map, self).__init__((width, height), *args, **kwargs)
        self._size = width
        self._map_surface = pygame.Surface((width, height))
        self._render_rect = render_rect
        text = settings.RobotoB[24].render(loading_type, True, settings.bright, (0, 0, 0))
        self.image.blit(text, (10, 10))

    def load_local_map(self):
        try:
            # Load the local image and scale it
            map_image = pygame.image.load("./images/worldmap/CompanionWorldMap.png").convert()
            map_surf = pygame.transform.scale(map_image, (1220, 1220))
            map_surf.fill((30, 150, 0), None, pygame.BLEND_RGBA_MULT)
            self._map_surface.blit(map_surf, (-310, -200))

        except Exception as e:
            print("Failed to load local map image:", e)

        self.redraw_map()

    def load_map(self, position, zoom, isWorld):
        self._fetching = threading.Thread(target=self._internal_load_map, args=(position, zoom, isWorld))
        self._fetching.start()

    def _internal_load_map(self, position, zoom, isWorld):
        self._mapper.load_map_coordinates(position, zoom, isWorld)
        self.redraw_map()

    def move_map(self, x, y):
        self._render_rect.move_ip(x, y)

    def redraw_map(self, coef=1):
        self.image.fill((0, 0, 0))

        self.image.blit(self._map_surface, (0, 0), area=self._render_rect)
