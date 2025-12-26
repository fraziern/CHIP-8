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


def draw(renderer, logical_x, logical_y):
    # draw a pixel
    x = PADDING + logical_x * (PIXWIDTH + PADDING)
    y = PADDING + logical_y * (PIXHEIGHT + PADDING)
    renderer.fill((x, y, PIXWIDTH, PIXHEIGHT), WHITE)


sdl2.ext.init()

window = sdl2.ext.Window("CHIP-8", size=(WIDTH, HEIGHT))
windowrenderer = sdl2.ext.Renderer(window)

window.show()

for x in range(LWIDTH):
    for y in range(LHEIGHT):
        draw(windowrenderer, x, y)


running = True
while(running):
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            running = False
            break
    sdl2.SDL_Delay(10)
    windowrenderer.present()

sdl2.ext.quit()