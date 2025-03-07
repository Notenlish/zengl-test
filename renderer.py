import zengl
import pygame
import importlib

from planets import BODIES

from shader_pipeline import ShaderPipeline, ShaderPipelinePostProc

from typing import TYPE_CHECKING
import os

if TYPE_CHECKING:
    from app import App


class Renderer:
    def __init__(self, app: "App") -> None:
        self.app = app
        self.mod = importlib.import_module("uniforms", "uniforms")

        self.planet_textures = {}
        self.load_planet_textures()
        self.latest_planet = None
        self.planet_id = None
        
        self.light_speed = 1.0

        self.bodyRadius = 100
        self.cloudRadius = 110
        self.planetPos = (0.5 * self.app.screen_size[0], 0.5 * self.app.screen_size[1])
        self.shouldMoveLight = True
        self.lightDirection = [0.3, 0.6, -1.0]
        self.isStar = False

    def setup(self):
        if not self.app.using_gpu:
            return

        self.shaders = {
            "rendering": {
                "vert": "shaders/default.vert",
                "frag": "shaders/water.frag",
            },
            "post_process": {
                "vert": "shaders/default.vert",
                "frag": "shaders/pixellize.frag",
            },
        }

        print("context creating")
        self.ctx = zengl.context()
        self.app.ctx = self.ctx

        # Note to self: if you dont use Texture in shader, glsl will complain,
        # but if you dont use these uniforms glsl wont complain

        self.load_uniforms()

        self.planet_normal_texture = pygame.image.load("normal.png").convert_alpha()
        self.planet_uv_texture = pygame.image.load("uv.png").convert_alpha()

        first_planet_name = list(self.planet_textures.keys())[0]
        first_planet_texture = self.planet_textures[first_planet_name]

        self.screen_shader = ShaderPipeline(
            self.app,
            self.uniforms_map,
            vert_shader_path=self.shaders["rendering"]["vert"],
            frag_shader_path=self.shaders["rendering"]["frag"],
            textures={
                "Texture": {
                    "dynamic": True,
                    "size": self.app.screen_size,
                },  # pg_surf will go here
                "planetTexture": {
                    "dynamic": False,
                    "img": first_planet_texture,
                    "size": first_planet_texture.get_size(),
                },
                "planetNormalTexture": {
                    "dynamic": False,
                    "img": self.planet_normal_texture,
                    "size": self.planet_normal_texture.get_size(),
                },
                "planetUVTexture": {
                    "dynamic": False,
                    "img": self.planet_uv_texture,
                    "size": self.planet_uv_texture.get_size(),
                },
            },
        )

        self.post_process = ShaderPipelinePostProc(
            self.app,
            self.uniforms_map,
            vert_shader_path=self.shaders["post_process"]["vert"],
            frag_shader_path=self.shaders["post_process"]["frag"],
            textures={
                "Texture": {
                    "dynamic": True,
                    "size": (320, 240),
                    "img": self.screen_shader.image_out,
                }
            },
        )

    def render(self):
        if self.app.using_gpu:
            # zengl
            self.ctx.new_frame()
            updated = {"Texture": self.app.pg_surf}
            if self.has_changed_planet:
                updated["planetTexture"] = self.planet_textures[self.latest_planet]

            self.screen_shader.image_out.clear()
            self.screen_shader.depth_out.clear()
            self.screen_shader.render(updated)

            self.post_process.image_out.clear()
            self.post_process.depth_out.clear()
            self.post_process.render({"Texture": self.screen_shader.image_out})

            self.post_process.image_out.blit()
            self.ctx.end_frame()

    def load_uniforms(self):
        self.mod = importlib.reload(self.mod)
        self.uniforms_map = self.mod.get_uniforms(self.app, self)

    def update_uniforms(self):
        self.screen_shader.uniforms, _, _ = self.screen_shader.pack_uniforms(
            self.uniforms_map
        )

    def load_planet_textures(self):
        for name, body in BODIES.items():
            img = pygame.image.load(f"planets/{name.lower()}.png").convert_alpha()
            self.planet_textures[name] = img

    def change_planet(self):
        # the uniform handling logic should be in a different class but oh well.
        self.planet_id += 1
        self.planet_id %= len(BODIES.keys())
        planet = BODIES[list(BODIES.keys())[self.planet_id]]
        self.app.camera.x = planet["bodyPos"].x
        self.app.camera.y = planet["bodyPos"].y

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

    def calculate_uniforms(self):
        # calculates uniforms for planet pos
        closest_dis = 999_999_999
        body_name = None
        cam_pos = pygame.Vector2(self.app.camera.x, self.app.camera.y)

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

    def reload_shaders(self):
        self.screen_shader.reload_shaders()
        self.post_process.reload_shaders()

    def reload_uniforms(self):
        self.load_uniforms()
        self.update_uniforms()  # send to shader
