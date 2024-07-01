from typing import TYPE_CHECKING, Dict, Literal

if TYPE_CHECKING:
    from main import App
    import pygame


def read_file(filename):
    with open(filename, "r") as f:
        data = f.read()
    return data


class ShaderPipeline:
    def __init__(
        self,
        app: "App",
        uniforms_map: Dict[any, any] = {},
        vert_shader_path: str = "default",
        frag_shader_path: str = "default",
        textures: Dict[str, Dict[str, any]] = {},
    ):
        self.app = app
        self.ctx = self.app.ctx
        self.textures = textures
        self.setup_images()
        self.uniforms, self.ufs_size, self.ufs_includes = self.pack_uniforms(
            uniforms_map
        )
        self.uniform_buffer = self.ctx.buffer(size=self.ufs_size)
        self.vert_shader_path = vert_shader_path
        self.frag_shader_path = frag_shader_path
        self.construct_pipeline()

    def setup_images(self):
        self.images = {}
        for tex_name, obj in self.textures.items():
            self.images[tex_name] = self.ctx.image(obj["size"], "rgba8unorm", samples=1)
            if obj.get("img"):  # if img is provided already
                screen_buffer = obj["img"].get_view("0").raw
                self.images[tex_name].write(screen_buffer)

    def construct_pipeline(self):
        layout, resources = self.get_resources_and_layout()
        vec2_screen_size_str = (
            f"vec2({self.app.screen_size[0]}.0, {self.app.screen_size[1]}.0)"
        )
        constants = {"constants": f"const vec2 iResolution = {vec2_screen_size_str};"}

        _includes = {}
        for _d in [constants, self.ufs_includes]:
            for k, v in _d.items():
                _includes[k] = v

        self.pipeline = self.ctx.pipeline(
            includes=_includes,
            vertex_shader=read_file(self.vert_shader_path),
            fragment_shader=read_file(self.frag_shader_path),
            layout=layout,
            resources=resources,
            framebuffer=None,
            topology="triangle_strip",
            viewport=(0, 0, self.app.screen_size[0], self.app.screen_size[1]),
            vertex_count=4,
            blend={
                "enable": True,
                "src_color": "src_alpha",
                "dst_color": "one_minus_src_alpha",
            },
        )

    def reload_shaders(self):
        print("reloading shaders!")
        self.construct_pipeline()

    def get_resources_and_layout(self):
        layout = [{"name": "Common", "binding": 0}]
        resources = [
            {"type": "uniform_buffer", "binding": 0, "buffer": self.uniform_buffer}
        ]
        i = 0
        for tex_name, obj in self.textures.items():
            layout.append({"name": tex_name, "binding": i})
            resources.append(
                {
                    "type": "sampler",
                    "binding": i,
                    "image": self.images[tex_name],
                    "min_filter": "nearest",
                    "mag_filter": "nearest",
                    "wrap_x": "clamp_to_edge",
                    "wrap_y": "clamp_to_edge",
                }
            )
            i += 1
        return layout, resources

    def render(self, surfaces: Dict[str, any]):
        self.update_uniforms()

        for tex_name, surf in surfaces.items():
            screen_buffer = surf.get_view("0").raw
            self.images[tex_name].write(screen_buffer)

        self.pipeline.render()

    def update_uniforms(self):
        if self.uniforms:
            for uniform in self.uniforms.values():
                self.uniform_buffer.write(uniform["value"](), offset=uniform["offset"])

    @staticmethod
    def pack_uniforms(
        uniforms_map: Dict[any, any]
    ) -> tuple[Dict[any, any], int, Dict[any, any]]:
        uniforms = {}
        layout = ""
        offset = 0
        for uf_name, uf_data in uniforms_map.items():
            uf_data: Dict[str, str]
            data_type = uf_data["glsl_type"]
            if data_type == "float":
                size = 4  # Size of a float in bytes
                align = 4
            elif data_type == "int":
                size = 4  # why dont you work...
                align = 4
            elif data_type == "vec2":
                size = 8  # 2 floats
                align = 8
            elif data_type == "vec3":
                size = 12  # 3 floats, but aligned as vec4 in std140 layout
                align = 16
            elif data_type == "vec4":
                size = 16  # 4 floats
                align = 16
            elif data_type == "mat4":
                size = 64  # 4x4 floats
                align = 16  # aligned as vec4 in std140 layout
            elif data_type == "ivec2":
                size = 8  # 2 i32
                align = 8
            elif data_type.startswith("vec3"):  # must be vec3 array
                arr_size = data_type.removeprefix("vec3[").removesuffix("]")
                size = 16 * int(arr_size)
                align = 16
            elif data_type.startswith("vec4"):  # must be vec4 array
                arr_size = data_type.removeprefix("vec4[").removesuffix("]")
                size = 16 * int(arr_size)  # untested but should work
                align = 16
            else:
                raise ValueError(
                    f"Either unknown GLSL type: {uf_data['glsl_type']} or not Implemented"
                )

            # Add padding for alignment
            if offset % align != 0:
                offset += align - (offset % align)

            uniforms[uf_name] = {"value": uf_data["value"], "offset": offset}
            offset += size
            layout += f"{uf_data['glsl_type']} {uf_name};\n"

        includes = f"""
                layout (std140) uniform Common {{{layout if uniforms else 'float dummy;'}}};
            """
        buffer_size = 16 + offset
        return uniforms, buffer_size, {"uniforms": includes.strip()}
