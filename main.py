# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "pygame-ce",
#   "numpy",
#   "struct",
#   "zengl",
#   "webcolors"
# ]
# ///
import numpy as np
import zengl
import struct

import pygame
import webcolors

import os
import asyncio

from shader_pipeline import ShaderPipeline

SHADER_TESTING = True

from app import App

if __name__ == "__main__":
    app = App()
    asyncio.run(app.run())
