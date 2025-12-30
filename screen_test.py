import sys
import sdl2.ext


# helper function to get list of bits from a byte
def _int_to_bits_bitwise(byte:int):
    bits_list = []
    for i in range(7, -1, -1):
        # Check if the bit at position 'i' is set (1) or not (0)
        bit = (byte >> i) & 1
        bits_list.append(bit)
    return bits_list


def _update_screen_row(screen_arr:list[list[int]], x:int, y:int, sprite_row:int) -> bool:
    if y >= len(screen_arr):
        raise ValueError("Out of range when drawing screen.")
    
    vf = False
    screen_row = screen_arr[y]
    bits_list = _int_to_bits_bitwise(sprite_row)

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
def update_screen(screen_arr:list[list[int]], x:int, y:int, sprite:bytearray) -> bool:
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
        if y >= len(screen_arr):
            break
        vf = _update_screen_row(screen_arr, x, y, row)
        y += 1
        
    return vf


#############################################################################################
# The below is all to test the 'update_screen' function, and prototype code for screen drawing
#############################################################################################
def main():
    # Logical width and height - the spec dimensions. Not necessarily the actual window dimensions
    LWIDTH = 64
    LHEIGHT = 32

    # Pixel size (physical)
    PIXWIDTH = 5
    PIXHEIGHT = 5

    PADDING = 1

    # Actual window width and height. Assuming pixels separated by padding
    WIDTH = (LWIDTH * PIXWIDTH) + ((LWIDTH + 1) * PADDING)
    HEIGHT = (LHEIGHT * PIXHEIGHT) + ((LHEIGHT + 1) * PADDING)

    WHITE = sdl2.ext.Color(255, 255, 255)
    BLACK = sdl2.ext.Color(0, 0, 0)


    def draw(renderer, logical_x, logical_y):
        # draw a pixel
        x = PADDING + logical_x * (PIXWIDTH + PADDING)
        y = PADDING + logical_y * (PIXHEIGHT + PADDING)
        renderer.fill((x, y, PIXWIDTH, PIXHEIGHT), WHITE)


    def drawscreen(renderer:sdl2.ext.Renderer, screen_arr:list[list[int]]):
        if len(screen_arr) < LHEIGHT:
            raise ValueError("Out of range when drawing screen.")
        
        renderer.clear(BLACK)

        for y in range(LHEIGHT):
            if len(screen_arr[y]) < LWIDTH:
                raise ValueError("Out of range when drawing screen.")
            
            for x in range(LWIDTH):
                if screen_arr[y][x]:
                    draw(renderer, x, y)

    # Create a memory map of the screen. This will hold literal 1s and 0s
    # We'll read/write to this, then pass this to a drawing function to refresh
    # the screen.
    mm_screen = [[0 for j in range(LWIDTH)] for i in range(LHEIGHT)]

    test_data = bytearray(b'\xff\x00\xff\x00')
    vf = update_screen(mm_screen, 0, 0, test_data)

    ### DRAWING
    sdl2.ext.init()

    window = sdl2.ext.Window("CHIP-8", size=(WIDTH, HEIGHT))
    windowrenderer = sdl2.ext.Renderer(window)

    window.show()

    # try drawing from memory map
    drawscreen(windowrenderer, mm_screen)

    running = True
    while(running):
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
        sdl2.SDL_Delay(10)
        windowrenderer.present()

    # pretty_print(memory)
    sdl2.ext.quit()


if __name__ == "__main__":
    main()

