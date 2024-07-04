import numpy as np
import zengl
import zengl_extras
import struct

import asyncio
import pygame
import os

from shader_pipeline import ShaderPipeline, ShaderPipelinePostProc
from camera import Camera
from renderer import Renderer

import importlib

UNCAPPED = False


class App:
    def __init__(self) -> None:

        pygame.init()
        self.using_gpu = True
        self.screen_size = (640, 480)
        try:
            zengl_extras.init(gpu=True, opengl_core=False)
            print("GPU=True")
        except:
            zengl_extras.init(gpu=False, opengl_core=False)
            
            
        self.pg_surf = self.init_screen()
        self.font = pygame.font.Font("renogare/Renogare-Regular.otf", 20)

        self.max_fps = 60 if not UNCAPPED else 1000
        self.camera = Camera(0, 0)
        
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.time_elapsed = 0
        self.time_speed = 1.0
        
        self.movement_speed = 500

        self.since_shader_check = 0

        self.renderer = Renderer(self)
        self.renderer.setup()

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
                "vsync": False,
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

    def update(self):
        # self.check_shader_change()
        self.move()
        self.renderer.calculate_uniforms()

    def render(self):
        # cpu drawing
        self.pg_draw()

        self.renderer.render()

        
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
                        self.renderer.reload_shaders()
                        self.renderer.reload_uniforms()
                    if event.key == pygame.K_F2:
                        self.renderer.change_planet()

            self.update()
            self.render()

            self.dt = self.clock.tick(self.max_fps) / 1000
            self.fps = self.clock.get_fps()
            fps = self.clock.get_fps()
            pygame.display.set_caption(
                f"Shaders in Browser Test | FPS:{fps:.0f} DT:{self.dt}"
            )
            self.time_elapsed += self.dt
            self.since_shader_check += self.dt

            pygame.display.flip()
            await asyncio.sleep(0)
