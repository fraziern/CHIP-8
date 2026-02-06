import pygame

# This will take care of memory mapping and displaying
class Display:
    LWIDTH = 64
    LHEIGHT = 32

    # Pixel size (physical)
    PIXWIDTH = 5
    PIXHEIGHT = 5

    PADDING = 1

    # Actual window width and height. Assuming pixels separated by padding
    WIDTH = (LWIDTH * PIXWIDTH) + ((LWIDTH + 1) * PADDING)
    HEIGHT = (LHEIGHT * PIXHEIGHT) + ((LHEIGHT + 1) * PADDING)

    WHITE = (255, 204, 2)
    BLACK = (153, 103, 0)

    FADEOUT = 50 # speed of pixel fade


    def __init__(self):
        # There are 2 "screens" here...
        # mm_screen     a memory map of a monochrome screen
        # window        a pygame display object

        self.mm_screen = [[0 for j in range(self.LWIDTH)] for i in range(self.LHEIGHT)]
        pygame.init()  # safe to call more than once

        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.window.fill(self.BLACK)

        self.pixel_surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        self.alpha_array = pygame.surfarray.array_alpha(self.pixel_surface)

        pygame.display.set_caption("CHIP-8")
        pygame.display.flip()


    
    # helper function to get list of bits from a byte
    def _int_to_bits_bitwise(self, byte:int):
        bits_list = []
        for i in range(7, -1, -1):
            # Check if the bit at position 'i' is set (1) or not (0)
            bit = (byte >> i) & 1
            bits_list.append(bit)
        return bits_list
    
    # helper function to update screen array with x/y coords
    def _update_screen_row(self, x:int, y:int, sprite_row:int) -> bool:
        if y >= len(self.mm_screen):
            raise ValueError("Out of range when drawing screen.")
        
        vf = False
        screen_row = self.mm_screen[y]
        bits_list = self._int_to_bits_bitwise(sprite_row)

        for bit in bits_list:
            if x >= len(screen_row):
                break
            if bit == 1:
                if screen_row[x] == 1:
                    screen_row[x] = 0
                    vf = True
                else: # screen_row[x] must be 0
                    screen_row[x] = 1
            x += 1

        return vf
    
    # update a "screen" array (memory mapped monochrome window, consisting of a 2D array of bits)
    # x,y - the coordinates to start the read/write
    # sprite - the sprite data to write (bytearray of up to 16 bytes)
    # returns True if any pixel was flipped from 1 to 0
    def update_screen(self, x:int, y:int, sprite:bytearray) -> bool:
        vf = False
        
        for row in sprite:
            if y >= len(self.mm_screen):
                break
            vf = self._update_screen_row(x, y, row) | vf
            y += 1
            
        return vf


    def _draw(self, logical_x, logical_y, should_fill:bool):
        # draw a pixel
        x = self.PADDING + logical_x * (self.PIXWIDTH + self.PADDING)
        y = self.PADDING + logical_y * (self.PIXHEIGHT + self.PADDING)
        pixel = pygame.Rect(x, y, self.PIXWIDTH, self.PIXHEIGHT)

        if should_fill:
            pygame.draw.rect(self.pixel_surface, self.WHITE, pixel)
        else: # fade
            current_alpha = int(self.alpha_array[x,y])
            faded_color = self.WHITE + (max(0, current_alpha - self.FADEOUT),)
            pygame.draw.rect(self.pixel_surface, faded_color, pixel)
            

    def clear_screen(self):
        self.mm_screen = [[0 for j in range(self.LWIDTH)] for i in range(self.LHEIGHT)]


    def render_screen(self):
        self.window.fill(self.BLACK)

        # get copy of alpha array for fading
        self.alpha_array = pygame.surfarray.array_alpha(self.pixel_surface)

        for y in range(self.LHEIGHT):            
            for x in range(self.LWIDTH):
                self._draw(x, y, self.mm_screen[y][x]) # draw to pixel_surface
        
        self.window.blit(self.pixel_surface, (0,0))
        pygame.display.flip()
    

    def quit(self):
        # Perform cleanup actions
        if self.window:
            pygame.quit() # This single call handles all sdl2.ext resources
