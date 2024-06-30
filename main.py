import numpy as np
import zengl
import struct

import asyncio
import pygame
import os

from shader_pipeline import ShaderPipeline

import subprocess

SHADER_TESTING = True

if __name__ == "__main__":
    from app import App
    app = App()
    asyncio.run(app.run())
