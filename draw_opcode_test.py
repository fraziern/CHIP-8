import sys
import sdl2.ext
from update_screen import update_screen, clear_screen, draw_screen
from Display import Display

sdl2.ext.init()

# instr will be a 2 byte opcode
def decode_instruction(instr:bytearray):
    if len(instr) != 2:
        print(f'instr:{instr}')
        raise ValueError("Instruction is the wrong size for decoding.")
    
    # nibbles
    n1 = (instr[0] >> 4) & 0xf
    n2 = instr[0] & 0xf
    n3 = (instr[1] >> 4) & 0xf
    n4 = instr[1] & 0xf

    nn = instr[1]

    nnn = (n2 << 8) | (n3 << 4) | n4

    return n1, n2, n3, n4, nn, nnn

# test_opcode = bytearray(b'\xff\xe0')
# n1, n2, n3, n4, nn, nnn = decode_instruction(test_opcode)
# print(f'n1: {n1:X} n2: {n2:X} n3: {n3:X} n4: {n4:X} nn: {nn:X} nnn: {nnn:X}')




    
def main():
    # Create a memory map of the screen. This will hold literal 1s and 0s
    # We'll read/write to this, then pass this to a drawing function to refresh
    # the screen.
    
    ROMSTART = 0x200
    index = 0
    registers = range(16)
    ram = bytearray(4096)


    # run instructions 00-09
    #####################################################
    ### load the IBM logo test rom
    filename = 'IBM Logo.ch8'

    with open(filename,'rb') as file:
        full_rom = file.read()

    ram[ROMSTART:ROMSTART + len(full_rom)] = full_rom

    ### DRAWING
    display = Display()

    # for i in range(ROMSTART, ROMSTART+0x0a, 2):
    #     n1, n2, n3, n4, nn, nnn = decode_instruction(ram[i:i+2])

    #     match n1:
    #         case 0x0:
    #             if nnn == 0x0e0:    # 00e0 clear screen
    #                 clear_screen(mm_screen)
    #                 draw_screen(windowrenderer, mm_screen)
    #         case 0xa:               # annn set index register I
    #             index = nnn
    #         case 0x6:               # 6xnn set register vx
    #             registers[n2] = nn
    #         case 0xd:               # dxyn draw
    #             x = registers[n2]
    #             y = registers[n3]
    #             sprite = ram[index:index+n4]
    #             update_screen(mm_screen, x, y, sprite)
    #             draw_screen(windowrenderer, mm_screen)

    display.update_screen(0, 0, bytearray(b'\xff\x00\xff'))

    running = True
    while(running):
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
        sdl2.SDL_Delay(10)
        display.render_screen()

    sdl2.ext.quit()


if __name__ == "__main__":
    main()
