from numba import njit
from enum import Enum
import numpy as np
import shutil
import os


##### Data Util #####

# List of sets of characters to use for the ASCII generation
ASCII_CHARS_TAB = [' .\'`^":;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$', ' _.,-=+:;cba!?0123456789$W#@Ñ', ' ixzao*#MW&8%B@$', ' .",:;!~+-xmo*#W&8@', '  12345678#@']

# Types of style
# Classic ASCII (no colour)
# ASCII with colour
# Pixel with colour
class OutputType(Enum):
    ASCII = 0
    ASCII_COLOUR = 1
    PIXEL_ART = 2

# Supported extentions
EXTENTIONS = ['.mp4', '.mov', '.mkv']


##### Image Conversion Functions #####

# Conversion of an image into classic ASCII
@njit(fastmath=True)
def accelerate_conversion_ascii(image: np.ndarray, width: int, height: int, ascii_coeff: float, skip_index: int) -> list:
    array_of_values = []
    for x in range(width):
        for y in range(height):
            char_index = int(image[x,y] * ascii_coeff)
            if char_index != skip_index:
                array_of_values.append((char_index, (x,y)))
    return array_of_values

# Conversion of an image into colour ASCII
@njit(fastmath=True)
def accelerate_conversion_ascii_colour(image: np.ndarray, gray_image: np.ndarray, width: int, height: int, ascii_coeff: float, colour_lvl: float, skip_index: int) -> list:
    array_of_values = []
    for x in range(width):
        for y in range(height):
            char_index = int(gray_image[x,y] * ascii_coeff)
            if char_index != skip_index:
                r, g, b = ((image[x,y] * (colour_lvl-1))/255)
                r = round(r) * 255//(colour_lvl-1)
                g = round(g) * 255//(colour_lvl-1)
                b = round(b) * 255//(colour_lvl-1)
                if r+g+b:
                    array_of_values.append((char_index, (r, g, b), (x,y)))
    return array_of_values

# Conversion of an image into pixel art with colour
@njit(fastmath=True)
def accelerate_conversion_pixel(image: np.ndarray, width: int, height: int, colour_lvl: float) -> list:
    array_of_values = []
    for x in range(0, width):
        for y in range(0, height):
            r, g, b = ((image[x,y] * (colour_lvl-1))/255)
            r = round(r) * 255//(colour_lvl-1)
            g = round(g) * 255//(colour_lvl-1)
            b = round(b) * 255//(colour_lvl-1)
            if r+g+b:
                array_of_values.append(((r, g, b), (x,y)))
    return array_of_values


##### Folder Managment Functions #####

# TODO Fix os.path.exists not detecting the folder
def createFolder() -> None:
    if os.path.exists('frames'):
        shutil.rmtree('frames', ignore_errors=True)
    
    os.mkdir('frames')

    if not os.path.exists('outputs'):
        os.mkdir('outputs')

def createVideo(videopath: str, audiopath: str, fps: int, width: int, height: int) -> None:
    os.system(f'ffmpeg -r {str(fps)} -f image2 -s {width}x{height} -i frames/{videopath}_%05d.png -i {audiopath} -map 0 -map 1:a -crf 25 -vcodec libx264 -pix_fmt yuv420p outputs/{videopath}.mp4')
    shutil.rmtree('frames', ignore_errors=True)