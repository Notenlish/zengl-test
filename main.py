# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "pygame-ce",
#   "numpy",
#   "struct",
#   "zengl",
#   "webcolors",
#   "zengl-extras"
# ]
# ///
import numpy as np
import zengl
import zengl_extras
import struct

import pygame
import webcolors

import os
import asyncio

import shader_pipeline

SHADER_TESTING = True

from app import App

if __name__ == "__main__":
    app = App()
    asyncio.run(app.run())
