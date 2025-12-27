import sys
import sdl2.ext

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


def drawscreen(renderer:sdl2.ext.Renderer, screen_arr):
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

# test pixel
mm_screen[0][10] = 1


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