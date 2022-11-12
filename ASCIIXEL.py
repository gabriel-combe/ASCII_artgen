from numba import njit
from enum import Enum
import pygame.gfxdraw
import pygame as pg
import numpy as np
import cv2

ASCII_CHARS_TAB = [' .\'`^":;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$', ' _.,-=+:;cba!?0123456789$W#@Ñ', ' ixzao*#MW&8%B@$', ' .",:;!~+-xmo*#W&8@', '  12345678#@']

class OutputType(Enum):
    ASCII = 'ascii'
    ASCII_COLOR = 'ascii_color'
    PIXEL_ART = 'pixel_art'

@njit(fastmath=True)
def accelerate_conversion_ascii(image: np.ndarray, width: int, height: int, ascii_coeff: float, step: int, skip_index: int) -> list:
    array_of_values = []
    for x in range(0, width, step[0]):
        for y in range(0, height, step[1]):
            char_index = int(image[x,y] * ascii_coeff)
            if char_index != skip_index:
                array_of_values.append((char_index, (x,y)))
    return array_of_values

@njit(fastmath=True)
def accelerate_conversion_ascii_color(image: np.ndarray, gray_image: np.ndarray, width: int, height: int, ascii_coeff: float, color_coeff: float, step: int, skip_index: int) -> list:
    array_of_values = []
    for x in range(0, width, step[0]):
        for y in range(0, height, step[1]):
            char_index = int(gray_image[x,y] * ascii_coeff)
            if char_index != skip_index:
                r, g, b = image[x,y]//color_coeff
                array_of_values.append((char_index, (r, g, b), (x,y)))
    return array_of_values

@njit(fastmath=True)
def accelerate_conversion_pixel(image: np.ndarray, width: int, height: int, color_coeff: float, step: int) -> list:
    array_of_values = []
    for x in range(0, width, step):
        for y in range(0, height, step):
            r, g, b = image[x,y]//color_coeff
            if r+g+b:
                array_of_values.append(((r, g, b), (x,y)))
    return array_of_values

class ASCIIXEL:
    def __init__(self, path, ascii_set=2, font_size=12, display_original=True, resolution=None, record=False, reverse_color=False, output_type=OutputType.ASCII, color_lvl=8, pixel_size=7) -> None:
        pg.init()

        self.path = path
        self.name = self.path.split('/')[1].split('.')[0]
        self.output_type = output_type
        self.reverse_color = reverse_color

        self.cap = cv2.VideoCapture(path)
        self.display_original = display_original
        self.RES = resolution
        self.image, _ = self.get_image()

        self.WIDTH, self.HEIGHT = self.image.shape[0], self.image.shape[1]
        self.original_ratio = self.HEIGHT/self.WIDTH
        if not self.RES: self.RES = self.WIDTH, self.HEIGHT
        else: self.WIDTH, self.HEIGHT = self.RES[0], self.RES[1]
        
        self.ratio = self.HEIGHT/self.WIDTH

        self.bg = 'white' if self.reverse_color else 'black'
        self.surface = pg.display.set_mode(self.RES)
        self.clock = pg.time.Clock()

        self.ASCII_CHARS = ASCII_CHARS_TAB[ascii_set]
        self.skip_index = 0
        if self.reverse_color: 
            self.ASCII_CHARS = self.ASCII_CHARS[::-1]
            self.skip_index = len(self.ASCII_CHARS)-1
        self.ASCII_COEFF = (len(self.ASCII_CHARS)-1)/255

        self.font_size = int(font_size * self.ratio/self.original_ratio)
        self.font = pg.font.SysFont('Courier', self.font_size, bold=True)

        self.CHAR_STEP = (int(self.font_size * 0.5), int(self.font_size * 0.8))
        self.PALETTE = [self.font.render(char, False, 'black' if self.reverse_color else 'white') for char in self.ASCII_CHARS]
        self.draw_char = self.draw_ascii
        self.COLOR_LVL = color_lvl

        if self.output_type == OutputType.ASCII_COLOR:
            self.PALETTE, self.COLOR_COEFF = self.create_palette()
            self.draw_char = self.draw_ascii_color
        elif self.output_type == OutputType.PIXEL_ART:
            self.PIXEL_SIZE = pixel_size
            self.PALETTE, self.COLOR_COEFF = self.create_palette()
            self.draw_char = self.draw_pixel

        self.rec_fps =  self.cap.get(cv2.CAP_PROP_FPS)
        self.record = record
        self.recorder = cv2.VideoWriter(f'outputs/ascii_{self.name}_{self.output_type.value}.mp4', cv2.VideoWriter_fourcc(*'mp4v'), self.rec_fps, self.RES)
    
    def get_frame(self) -> np.ndarray:
        frame = pg.surfarray.array3d(self.surface)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return cv2.transpose(frame)
    
    def record_frame(self) -> None:
        if self.record:
            frame = self.get_frame()
            self.recorder.write(frame)
            cv2.imshow(f'outputs/ascii_{self.name}_{self.output_type.value}.mp4', frame)
            if cv2.waitKey(1) & 0xFF == 27:
                self.record = not self.record
                cv2.destroyAllWindows()
    
    def draw_ascii(self) -> None:
        _, gray_image = self.get_image()
        array_of_values = accelerate_conversion_ascii(gray_image, self.WIDTH, self.HEIGHT, self.ASCII_COEFF, self.CHAR_STEP, self.skip_index)
        for char_index, pos in array_of_values:
            self.surface.blit(self.PALETTE[char_index], pos)
    
    def draw_ascii_color(self) -> None:
        image, gray_image = self.get_image()
        array_of_values = accelerate_conversion_ascii_color(image, gray_image, self.WIDTH, self.HEIGHT, self.ASCII_COEFF, self.COLOR_COEFF, self.CHAR_STEP, self.skip_index)
        for char_index, color, pos in array_of_values:
            char = self.ASCII_CHARS[char_index]
            self.surface.blit(self.PALETTE[char][color], pos)
    
    def draw_pixel(self) -> None:
        image, _ = self.get_image()
        array_of_values = accelerate_conversion_pixel(image, self.WIDTH, self.HEIGHT, self.COLOR_COEFF, self.PIXEL_SIZE)
        for color_key, (x, y) in array_of_values:
            pygame.gfxdraw.box(self.surface, (x, y, self.PIXEL_SIZE, self.PIXEL_SIZE), self.PALETTE[color_key])
        
    def create_palette(self) -> tuple[dict, int]:
        colors, color_coeff = np.linspace(0, 255, num=self.COLOR_LVL, dtype=int, retstep=True)
        color_coeff = int(color_coeff)

        color_palette = [np.array([r, g, b]) for r in colors for g in colors for b in colors]

        palette_char = dict.fromkeys(self.ASCII_CHARS, None)
        palette_pixel = {}

        for char in palette_char:
            char_palette = {}
            for color in color_palette:
                color_key = tuple(color // color_coeff)
                char_palette[color_key] = self.font.render(char, False, tuple(color))
                palette_pixel[color_key] = color

            if self.output_type == OutputType.PIXEL_ART: break
            palette_char[char] = char_palette

        return palette_char if not self.output_type == OutputType.PIXEL_ART else palette_pixel, color_coeff

    def get_image(self) -> tuple[np.ndarray, np.ndarray]:
        ret, self.cv2_image = self.cap.read()
        if not ret: exit()
        if self.RES: self.cv2_image = cv2.resize(self.cv2_image, self.RES, interpolation=cv2.INTER_AREA)
        transposed_image = cv2.transpose(self.cv2_image)
        image = cv2.cvtColor(transposed_image, cv2.COLOR_BGR2RGB)
        gray_image = cv2.cvtColor(transposed_image, cv2.COLOR_BGR2GRAY)
        return image, gray_image
    
    def draw_cv2_image(self) -> None:
        resized_cv2_image = cv2.resize(self.cv2_image, (720, int(720 * self.ratio)), interpolation=cv2.INTER_AREA)
        cv2.imshow('img', resized_cv2_image)
    
    def draw(self) -> None:
        self.surface.fill(self.bg)
        self.draw_char()
        if self.display_original: self.draw_cv2_image()
    
    def save_image(self) -> None:
        pygame_image = pg.surfarray.array3d(self.surface)
        cv2_img = cv2.transpose(pygame_image)
        cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(f'outputs/ascii_{self.name}_{self.output_type.value}.jpg', cv2_img)
    
    def run(self) -> None:
        while True:
            for i in pg.event.get():
                if i.type == pg.QUIT: exit()
                elif i.type == pg.KEYDOWN:
                    if i.key == pg.K_s: self.save_image()
                    if i.key == pg.K_r: self.record = not self.record
            
            self.record_frame()
            self.draw()
            pg.display.set_caption(str(self.clock.get_fps()))
            pg.display.flip()
            self.clock.tick(self.rec_fps if not self.record else 0)

if __name__ == '__main__':
    app = ASCIIXEL(path='videos/Touhou-Bad_Apple!!.mp4', resolution=(80*6, 45*9), ascii_set=4, display_original=True, reverse_color=True, output_type=OutputType.ASCII, record=True)
    app.run()

    