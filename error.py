import zengl
import pygame


class App:
    def __init__(self) -> None:
        pygame.init()
        self.gpu = True
        self.pg_surf = pygame.display.set_mode(
            (200, 200),
            pygame.DOUBLEBUF | pygame.OPENGL if self.gpu else 0,
            vsync=True,
        ).convert_alpha()
        self.clock = pygame.time.Clock()

        if self.gpu:
            self.gpu_setup()

    def gpu_setup(self):
        self.ctx = zengl.context()

        self.gl_image = self.ctx.image(self.pg_surf.get_size(), "rgba8unorm")

        # {"type": "uniform_buffer", "binding": 0, "buffer": self.uniform_buffer},
        # {"name": "Common", "binding": 0},
        layout = [{"name": "Texture", "binding": 0}]
        resources = [
            {
                "type": "sampler",
                "binding": 0,
                "image": self.gl_image,
                "min_filter": "nearest",
                "mag_filter": "nearest",
                "wrap_x": "clamp_to_edge",
                "wrap_y": "clamp_to_edge",
            },
        ]

        self.pipeline = self.ctx.pipeline(
            vertex_shader="""#version 300 es
precision highp float;

vec2 vertex[4] = vec2[](
    vec2(-1.0, -1.0),
    vec2(-1.0, 1.0),
    vec2(1.0, -1.0),
    vec2(1.0, 1.0)
);

out vec2 fragCoord;

void main() {
    fragCoord = vertex[gl_VertexID] * vec2(0.5, -0.5) + 0.5;
    gl_Position = vec4(vertex[gl_VertexID], 0.0, 1.0);
}
            """,
            fragment_shader="""#version 300 es
precision highp float;

uniform sampler2D Texture;

in vec2 fragCoord;
out vec4 fragColor;

void main() {
    vec4 color = texture(Texture, fragCoord).bgra;
    fragColor = color;
}
            """,
            layout=layout,
            resources=resources,
            framebuffer=None,
            topology="triangle_strip",
            viewport=(0, 0, self.pg_surf.get_width(), self.pg_surf.get_height()),
            vertex_count=4,
            blend={
                "enable": True,
                "src_color": "src_alpha",
                "dst_color": "one_minus_src_alpha",
            },
        )

    def draw(self):
        self.pg_surf.fill("black")
        pygame.draw.circle(self.pg_surf, "white", (100, 100), 10.0)

        if self.gpu:
            self.ctx.new_frame()

            screen_buffer = self.pg_surf.get_view("0").raw
            self.gl_image.write(screen_buffer)

            self.pipeline.render()
            self.ctx.end_frame()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

            self.draw()

            pygame.display.set_caption(f"FPS:{self.clock.get_fps()}")
            self.clock.tick(60)

            pygame.display.flip()


app = App()
app.run()
