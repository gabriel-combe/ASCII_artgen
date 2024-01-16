# ASCII_artgen

ASCIIXEL can generate images an videos using ASCII character or large pixels (with the option to add colour)

https://www.youtube.com/watch?v=nAvhP0ASKRY

## Installation

Only python is needed, with numpy, OpenCV, and Pygame libraries.

## Usage example

Run the ASCIIXEL python file to start the generation.
To modify the video to convert and the parameters of the generator, change the following line:

```py
app = ASCIIXEL(path='YOUR_VIDEO', ascii_set=2, display_original=False, reverse_colour=False, output_type=OutputType.ASCII_COLOUR, record=True)
```

> I will add argument parser in the futur.

## Meta

[Gabriel Combe-Ounkham](https://github.com/gabriel-combe)

Distributed under the GNU GENERAL PUBLIC license. See ``LICENSE`` for more information.