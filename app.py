import numpy as np
import zengl
import zengl_extras
import struct

import asyncio
import pygame
import os

from shader_pipeline import ShaderPipeline
from camera import Camera
from planets import BODIES

import importlib

UNCAPPED = True


class App:
    def __init__(self) -> None:
        self.mod = importlib.import_module("uniforms", "uniforms")

        pygame.init()
        self.using_gpu = True
        self.screen_size = (720, 405)
        try:
            zengl_extras.init(gpu=True)
        except:
            zengl_extras.init(gpu=False)
            
        self.pg_surf = self.init_screen()
        self.font = pygame.font.Font("renogare/Renogare-Regular.otf", 20)

        self.max_fps = 60 if not UNCAPPED else 1000
        self.camera = Camera(0, 0)
        
        self.planet_textures = {}
        self.load_planet_textures()
        self.latest_planet = None
        self.planet_id = None
        first_planet_name = list(self.planet_textures.keys())[0]

        self.bodyRadius = 100
        self.cloudRadius = 110
        self.planetPos = (0.5 * self.screen_size[0], 0.5 * self.screen_size[1])
        self.shouldMoveLight = True
        self.lightDirection = [0.3, 0.6, -1.0]
        self.movement_speed = 500
        self.isStar = False
        

        self.clock = pygame.time.Clock()
        self.dt = 0
        self.time_elapsed = 0
        self.past_fps = []
        self.screenshot = pygame.image.load("screenshot.png").convert()

        self.shaders = {"vert": "default.vert", "frag": "planet4.frag"}
        self.since_shader_check = 0

        if self.using_gpu:
            self.setup_gpu()

    def load_uniforms(self):
        self.mod = importlib.reload(self.mod)
        self.uniforms_map = self.mod.get_uniforms(self)

    def update_uniforms(self):
        self.screen_shader.uniforms, _, _ = self.screen_shader.pack_uniforms(
            self.uniforms_map
        )
    
    def load_planet_textures(self):
        for name, body in BODIES.items():
            img = pygame.image.load(f"{name.lower()}.png").convert_alpha()    
            self.planet_textures[name] = img
    
    def setup_gpu(self):
        self.ctx = zengl.context()

        # Note to self: if you dont use Texture in shader, glsl will complain,
        # but if you dont use these uniforms glsl wont complain

        self.load_uniforms()

        self.planet_normal_texture = pygame.image.load("normal.png").convert_alpha()
        self.planet_uv_texture = pygame.image.load("uv.png").convert_alpha()

        first_planet_name = list(self.planet_textures.keys())[0]
        first_planet_texture = self.planet_textures[first_planet_name]

        self.screen_shader = ShaderPipeline(
            self,
            self.uniforms_map,
            vert_shader_path=self.shaders["vert"],
            frag_shader_path=self.shaders["frag"],
            textures={
                "Texture": {
                    "dynamic": True,
                    "size": self.screen_size,
                },  # pg_surf will go here
                "planetTexture": {
                    "dynamic": False,
                    "img": first_planet_texture,
                    "size": first_planet_texture.get_size(),
                },
                "planetNormalTexture": {
                    "dynamic":False,
                    "img": self.planet_normal_texture,
                    "size": self.planet_normal_texture.get_size()
                },
                "planetUVTexture": {
                    "dynamic":False,
                    "img": self.planet_uv_texture,
                    "size": self.planet_uv_texture.get_size()
                }
            },
        )

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.camera.y -= self.movement_speed * self.dt
        if keys[pygame.K_a]:
            self.camera.x -= self.movement_speed * self.dt
        if keys[pygame.K_s]:
            self.camera.y += self.movement_speed * self.dt
        if keys[pygame.K_d]:
            self.camera.x += self.movement_speed * self.dt

    def init_screen(self):
        if self.using_gpu:
            display_kwargs = {
                "size": self.screen_size,
                "flags": pygame.OPENGL | pygame.DOUBLEBUF,
                "vsync": not UNCAPPED,
            }
            # pygame needs to use RGBA mode otherwise it wont work with opengl
            try:
                return pygame.display.set_mode(**display_kwargs).convert_alpha()
            except:
                del display_kwargs["vsync"]
                return pygame.display.set_mode(**display_kwargs).convert_alpha()
        else:
            try:
                return pygame.display.set_mode(size=self.screen_size, vsync=True)
            except:
                return pygame.display.set_mode(size=self.screen_size, vsync=False)

    def check_shader_change(self):
        if self.since_shader_check > 1:  # check every second
            self.load_uniforms()
            self.update_uniforms()  # send to shader

            self.since_shader_check = 0
            if not hasattr(self, "shader_history"):
                self.shader_history = {
                    shader_path: os.stat(shader_path).st_mtime
                    for shader_path in self.shaders.values()
                }
            for _type, shader_path in self.shaders.items():
                file_mod_time = os.stat(shader_path).st_mtime
                if file_mod_time > self.shader_history[shader_path]:
                    self.shader_history[shader_path] = file_mod_time
                    self.screen_shader.reload_shaders()
                    # just reload using F1

    def update(self):
        # self.check_shader_change()
        self.move()
        self.calculate_uniforms()

    def render(self):
        # cpu drawing
        self.pg_draw()

        if self.using_gpu:
            # zengl
            self.ctx.new_frame()
            updated = {"Texture": self.pg_surf}
            if self.has_changed_planet:
                updated["planetTexture"] = self.planet_textures[self.latest_planet]
            self.screen_shader.render(updated)
            self.ctx.end_frame()

    def calculate_uniforms(self):
        # calculates uniforms for planet pos
        closest_dis = 999_999_999
        body_name = None
        cam_pos = pygame.Vector2(self.camera.x, self.camera.y)
        
        for name, body in BODIES.items():
            bodypos: pygame.Vector2 = body["bodyPos"]
            dis = cam_pos - bodypos
            if dis.length() < closest_dis:
                closest_dis = dis.length()
                body_name = name
        
        body = BODIES[body_name]
        self.bodyRadius = body["bodyRadius"]
        self.cloudRadius = body["cloudRadius"]
        self.planetPos = body["bodyPos"] - cam_pos
        self.lightDirection = body["lightDirection"]
        self.isStar = body.get("isStar", False)
        self.has_changed_planet = True if self.latest_planet != body_name else False
        self.latest_planet = body_name
        self.planet_id = list(BODIES.keys()).index(body_name)

    def pg_draw(self):
        self.pg_surf.fill("#222222")

        surf = self.font.render(f"{self.camera.x}, {self.camera.y}", True, "white")
        self.pg_surf.blit(surf, (0, 0))

    async def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.MOUSEMOTION:
                    self.planetPos = pygame.mouse.get_pos()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F1:
                        self.screen_shader.reload_shaders()
                        self.load_uniforms()
                        self.update_uniforms()  # send to shader
                    if event.key == pygame.K_F2:
                        self.planet_id += 1
                        self.planet_id %= len(BODIES.keys())
                        planet = BODIES[list(BODIES.keys())[self.planet_id]]
                        self.camera.x = planet["bodyPos"].x
                        self.camera.y = planet["bodyPos"].y

            self.update()
            self.render()

            self.dt = self.clock.tick(self.max_fps) / 1000
            self.fps = self.clock.get_fps()
            fps = self.clock.get_fps()
            self.past_fps.append(fps)
            avg = 0
            for fps in self.past_fps:
                avg += fps
            avg /= len(self.past_fps)
            if len(self.past_fps) > 60:
                self.past_fps.pop(0)
            
            pygame.display.set_caption(
                f"Shaders in Browser Test | Avg FPS:{avg:.0f} FPS:{fps:.0f} DT:{self.dt}"
            )
            self.time_elapsed += self.dt
            self.since_shader_check += self.dt

            pygame.display.flip()
            await asyncio.sleep(0)
