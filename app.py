import numpy as np
import zengl
import struct

import asyncio
import pygame
import os

from shader_pipeline import ShaderPipeline
import importlib


class App:
    def __init__(self) -> None:
        self.mod = importlib.import_module("uniforms", "uniforms")

        pygame.init()
        self.screen_size = (1280, 720)
        self.using_gpu = True
        self.max_fps = 60

        self.bodyRadius = 100
        self.cloudRadius = 110
        self.planetPos = (0.5 * self.screen_size[0], 0.5 * self.screen_size[1])

        self.pg_surf = self.init_screen()
        pygame.display.set_caption("Shaders in Browser Test")
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.time_elapsed = 0
        self.screenshot = pygame.image.load("screenshot.png").convert()

        self.shaders = {"vert": "default.vert", "frag": "planet.frag"}
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

    def setup_gpu(self):
        self.ctx = zengl.context()

        # Note to self: if you dont use Texture in shader, glsl will complain,
        # but if you dont use these uniforms glsl wont complain

        self.load_uniforms()

        self.planet_texture = pygame.image.load("earth.png").convert_alpha()

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
                    "img": self.planet_texture,
                    "size": self.planet_texture.get_size(),
                },
            },
        )

    def init_screen(self):
        if self.using_gpu:
            display_kwargs = {
                "size": self.screen_size,
                "flags": pygame.OPENGL | pygame.DOUBLEBUF,
                "vsync": True,
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
                    # self.screen_shader.reload_shaders()
                    # just reload using F1

    def update(self):
        self.check_shader_change()

    def render(self):
        # cpu drawing
        self.pg_draw()

        if self.using_gpu:
            # zengl
            self.ctx.new_frame()
            self.screen_shader.render({"Texture": self.pg_surf})
            self.ctx.end_frame()

    def pg_draw(self):
        self.pg_surf.fill("black")
        self.pg_surf.blit(self.screenshot, (100, 100))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F1:
                        self.screen_shader.reload_shaders()
                        self.load_uniforms()
                        self.update_uniforms()  # send to shader

            self.update()
            self.render()

            self.dt = self.clock.tick(self.max_fps) / 1000
            self.fps = self.clock.get_fps()
            self.time_elapsed += self.dt
            self.since_shader_check += self.dt

            pygame.display.flip()
