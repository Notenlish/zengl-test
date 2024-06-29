import zengl
import struct

import asyncio
import pygame

from shader_pipeline import ShaderPipeline


def read_file(filename):
    with open(filename, "r") as f:
        data = f.read()
    return data


def surf_to_tex(surface: pygame.Surface, ctx: zengl.Context):
    # 1 = NEAREST(for pixel art)
    tex = ctx.image(
        surface.get_size(), format="rgba8unorm", data=surface.get_view("1"), samples=1
    )
    tex.filter = (zengl.NEAREST, zengl.NEAREST)
    tex.write(surface.get_view("1"))
    return tex


pygame.init()

vert_shader = read_file("vertex_shader.vert")
frag_shader = read_file("underwater2.frag")


class App:
    def __init__(self) -> None:
        self.screen_size = (960, 540)
        self.pg_surf = self.init_screen()
        pygame.display.set_caption("Shaders in Browser Test")
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.time_elapsed = 0
        self.screenshot = pygame.image.load("screenshot.png").convert()

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

    def update(self):
        pass

    def render(self):
        # cpu drawing
        self.pg_draw()

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

            self.dt = self.clock.tick(60) / 1000
            self.fps = self.clock.get_fps()
            self.time_elapsed += self.dt
            print(self.fps, self.dt)

            pygame.display.flip()
            await asyncio.sleep(0)


if __name__ == "__main__":
    app = App()
    asyncio.run(app.run())
