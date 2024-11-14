from PIL import Image, ImageFont, ImageDraw
from utils import ASCII_CHARS_TAB, OutputType, accelerate_conversion_ascii, accelerate_conversion_ascii_colour, accelerate_conversion_pixel, createFolder, createVideo
import numpy as np
import cv2


# ASCIIXEL class for images and videos ASCII conversion
class ASCIIXEL:
    def __init__(self, path='', ascii_set=2, element_size=12, display_original=False, resolution=None, record=False, reverse_colour=False, output_type=OutputType.ASCII, colour_lvl=8) -> None:
        self.path = path
        self.output_type = output_type
        self.reverse_colour = reverse_colour
        self.custom_resolution = resolution
        self.display_original = display_original
        self.ascii_set = ascii_set
        self.record = record

        self.WIDTH = None
        self.nb_frame = 0
        self.finish = False

        # Character settings
        self.draw_char = self.draw_ascii
        self.colour_lvl = colour_lvl

        # Character display settings
        self.element_size = element_size

    # TODO Discard the first frame (glitch)
    def setup(self) -> bool:
        if self.path == '': return False

        self.name = self.path.split('/')[-1].split('.')[0]
        self.current_element_size = self.element_size
        self.output_name = f'ASCIIXEL_{self.name}_{self.output_type.name}_elSize{self.current_element_size}'
        if self.output_type != OutputType.PIXEL_ART:
            self.output_name += f'_asciiPal{self.ascii_set}'

        if self.output_type != OutputType.ASCII:
            self.output_name += f'_colourLvl{self.colour_lvl}'
        
        # Video/Image setup
        self.cap = cv2.VideoCapture(self.path)
        self.get_image()

        # Character display settings
        self.font = ImageFont.load_default()

        # Screen settings
        if self.custom_resolution:
            self.ORIGWIDTH, self.ORIGHEIGHT = self.custom_resolution
        else:
            self.ORIGWIDTH, self.ORIGHEIGHT = self.image.shape[0], self.image.shape[1]

        self.WIDTH, self.HEIGHT = self.ORIGWIDTH//self.current_element_size, self.ORIGHEIGHT//self.current_element_size

        self.original_ratio = self.ORIGHEIGHT/self.ORIGWIDTH
        self.ratio = self.HEIGHT/self.WIDTH

        # Resize first frame
        self.image = cv2.resize(self.image, (self.WIDTH, self.HEIGHT), interpolation=cv2.INTER_AREA)
        self.grayscale = cv2.resize(self.grayscale, (self.WIDTH, self.HEIGHT), interpolation=cv2.INTER_AREA)

        # Display settings
        self.bg = 'white' if self.reverse_colour else 'black'
        self.fg = 'black' if self.reverse_colour else 'white'

        # Selection of the character sets
        self.ASCII_CHARS = ASCII_CHARS_TAB[self.ascii_set]

        # Reverse the ASCII density if reverse_colour argument is true
        self.skip_index = 0
        if self.reverse_colour: 
            self.ASCII_CHARS = self.ASCII_CHARS[::-1]
            self.skip_index = len(self.ASCII_CHARS)-1
        self.ASCII_COEFF = (len(self.ASCII_CHARS)-1)/255

        # Selection of the style
        if self.output_type == OutputType.ASCII:
            self.draw_char = self.draw_ascii
        if self.output_type == OutputType.ASCII_COLOUR:
            self.draw_char = self.draw_ascii_colour
        elif self.output_type == OutputType.PIXEL_ART:
            self.draw_char = self.draw_pixel

        # Create output image
        self.out_image = Image.new('RGB', (self.ORIGWIDTH, self.ORIGHEIGHT), self.bg)
        self.img_draw = ImageDraw.Draw(self.out_image)

        # Recording settings
        self.rec_fps =  self.cap.get(cv2.CAP_PROP_FPS)
        
        if self.record:
            createFolder()

        return True
    
    def reset(self) -> None:
        self.WIDTH = None
        self.nb_frame = 0
        self.finish = False
    
    # Retrieve a frame from a video/image
    def get_image(self) -> None:
        ret, self.cv2_image = self.cap.read()
        if not ret:
            self.finish = True
            return

        if self.custom_resolution: self.cv2_image = cv2.resize(self.cv2_image, (self.ORIGWIDTH, self.ORIGHEIGHT), interpolation=cv2.INTER_AREA)
        self.cv2_image = cv2.cvtColor(self.cv2_image, cv2.COLOR_BGR2RGB)

        resized_img = self.cv2_image
        if self.WIDTH: resized_img = cv2.resize(resized_img, (self.WIDTH, self.HEIGHT), interpolation=cv2.INTER_AREA)
        self.image = cv2.transpose(resized_img)
        self.grayscale = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

    # Draw the classic ASCII
    def draw_ascii(self) -> None:
        array_of_values = accelerate_conversion_ascii(self.grayscale, self.WIDTH, self.HEIGHT, self.ASCII_COEFF, self.skip_index)
        for char_index, (x, y) in array_of_values:
            self.img_draw.text((x*self.current_element_size, y*self.current_element_size), self.ASCII_CHARS[char_index], fill=self.fg, font=self.font, font_size=self.current_element_size)
    
    # Draw the colour ASCII
    def draw_ascii_colour(self) -> None:
        array_of_values = accelerate_conversion_ascii_colour(self.image, self.grayscale, self.WIDTH, self.HEIGHT, self.ASCII_COEFF, self.colour_lvl, self.skip_index)
        for char_index, colour, (x, y) in array_of_values:
            self.img_draw.text((x*self.current_element_size, y*self.current_element_size), self.ASCII_CHARS[char_index], fill=colour, font=self.font, font_size=self.current_element_size)
    
    # Draw the pixel art
    def draw_pixel(self) -> None:
        array_of_values = accelerate_conversion_pixel(self.image, self.WIDTH, self.HEIGHT, self.colour_lvl)
        for colour, (x, y) in array_of_values:
            self.img_draw.rectangle(
                [
                    x*self.current_element_size,
                    y*self.current_element_size,
                    (x*self.current_element_size)+self.current_element_size,
                    (y*self.current_element_size)+self.current_element_size
                ], fill=colour)

    # Draw the converted frame
    def draw(self) -> None:
        self.out_image = Image.new('RGB', (self.ORIGWIDTH, self.ORIGHEIGHT), self.bg)
        self.img_draw = ImageDraw.Draw(self.out_image)

        self.draw_char()
        self.get_image()

    # Save an image
    def save_image(self) -> None:
        self.out_image.save(f'frames/{self.output_name}_{self.nb_frame:05d}.png')

    # Convert all the frames into a video if record is true
    def record_video(self) -> None:
        if self.record:
            createVideo(self.output_name, self.path, self.rec_fps, self.ORIGWIDTH, self.ORIGHEIGHT)

    # Run one step of the algorithm
    def runStep(self) -> bool:
        if self.finish: return self.finish

        self.draw()

        if self.finish: return self.finish

        if self.record:
            self.save_image()

        self.nb_frame += 1

    # Run the main algorithm
    def run(self) -> None:
        if not setup(): return

        while not self.finish:
            self.runStep()
        
        record_video()