import zengl
import struct

import asyncio
import pygame

from shader_pipeline import ShaderPipeline


def read_file(filename):
    with open(filename, "r") as f:
        data = f.read()
    return data


pygame.init()

vert_shader = read_file("vertex_shader.vert")
frag_shader = read_file("underwater3.frag")


class App:
    def __init__(self) -> None:
        self.screen_size = (960, 540)
        self.using_gpu = False
        self.max_fps = 60

        self.pg_surf = self.init_screen()
        pygame.display.set_caption("Shaders in Browser Test")
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.time_elapsed = 0
        self.screenshot = pygame.image.load("screenshot.png").convert()

        if self.using_gpu:
            self.ctx = zengl.context()

            uniforms_map = {
                "time": {
                    "value": lambda: struct.pack("f", self.time_elapsed),
                    "glsl_type": "float",
                }
            }

            self.screen_shader = ShaderPipeline(
                self, uniforms_map, vert_shader, frag_shader
            )

    def init_screen(self):
        if self.using_gpu:
            display_kwargs = {
                "size": self.screen_size,
                "flags": pygame.OPENGL | pygame.DOUBLEBUF,
                "vsync": True,
            }
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
        pass

    def render(self):
        # cpu drawing
        self.pg_draw()

        if self.using_gpu:
            # zengl
            self.ctx.new_frame()
            self.screen_shader.render(self.pg_surf)
            self.ctx.end_frame()

    def pg_draw(self):
        self.pg_surf.fill("black")
        self.pg_surf.blit(self.screenshot, pygame.mouse.get_pos())

    async def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

            self.update()
            self.render()

            self.dt = self.clock.tick(self.max_fps) / 1000
            self.fps = self.clock.get_fps()
            self.time_elapsed += self.dt

            pygame.display.flip()
            await asyncio.sleep(0)


if __name__ == "__main__":
    app = App()
    asyncio.run(app.run())
