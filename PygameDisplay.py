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


    def __init__(self):
        self.mm_screen = [[0 for j in range(self.LWIDTH)] for i in range(self.LHEIGHT)]
        pygame.init()  # safe to call more than once

        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("CHIP-8")

        self.window.fill(self.BLACK)
        pygame.display.flip()

    
    # helper function to get list of bits from a byte
    def _int_to_bits_bitwise(self, byte:int):
        bits_list = []
        for i in range(7, -1, -1):
            # Check if the bit at position 'i' is set (1) or not (0)
            bit = (byte >> i) & 1
            bits_list.append(bit)
        return bits_list
    

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
    # screen_arr - the screen array to read/write
    # x,y - the coordinates to start the read/write
    # sprite - the sprite data to write (bytearray of up to 16 bytes)
    # returns True if any pixel was flipped from 1 to 0
    def update_screen(self, x:int, y:int, sprite:bytearray) -> bool:
        vf = False

        # For N rows:
        #     Get the Nth byte of sprite data, counting from the memory address in the I register (I is not incremented)
        #     For each of the 8 pixels/bits in this sprite row (from left to right, ie. from most to least significant bit):
        #         If the current pixel in the sprite row is on and the pixel at coordinates X,Y on the screen is also on, turn off the pixel and set VF to 1
        #         Or if the current pixel in the sprite row is on and the screen pixel is not, draw the pixel at the X and Y coordinates
        #         If you reach the right edge of the screen, stop drawing this row
        #         Increment X (VX is not incremented)
        #     Increment Y (VY is not incremented)
        #     Stop if you reach the bottom edge of the screen
        
        for row in sprite:
            if y >= len(self.mm_screen):
                break
            vf = self._update_screen_row(x, y, row)
            y += 1
            
        return vf


    def clear_screen(self):
        self.mm_screen = [[0 for j in range(self.LWIDTH)] for i in range(self.LHEIGHT)]
        self.window.fill(self.BLACK)


    def _draw(self, logical_x, logical_y):
        # draw a pixel
        x = self.PADDING + logical_x * (self.PIXWIDTH + self.PADDING)
        y = self.PADDING + logical_y * (self.PIXHEIGHT + self.PADDING)
        pixel = pygame.Rect(x, y, self.PIXWIDTH, self.PIXHEIGHT)
        pygame.draw.rect(self.window, self.WHITE, pixel)


    def render_screen(self):        
        self.window.fill(self.BLACK)

        for y in range(self.LHEIGHT):            
            for x in range(self.LWIDTH):
                if self.mm_screen[y][x]:
                    self._draw(x, y)
        
        pygame.display.flip()
    

    def quit(self):
        # Perform cleanup actions
        if self.window:
            pygame.quit() # This single call handles all sdl2.ext resources
