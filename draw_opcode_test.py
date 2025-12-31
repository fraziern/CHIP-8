import sys
import sdl2.ext
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

    
def main():
    # Create a memory map of the screen. This will hold literal 1s and 0s
    # We'll read/write to this, then pass this to a drawing function to refresh
    # the screen.
    
    ROMSTART = 0x200
    index = 0
    registers = [i for i in range(16)]
    pc = ROMSTART
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

    running = True
    while(running):
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
        sdl2.SDL_Delay(10)

        instr = ram[pc:pc+2]
        pc += 2
        
        n1, n2, n3, n4, nn, nnn = decode_instruction(instr)

        match n1:
            case 0x0:
                if nnn == 0x0e0:    # 00e0 clear screen
                    display.clear_screen()
            case 0x1:               # 1nnn jump
                pc = nnn
            case 0x6:               # 6xnn set register vx
                registers[n2] = nn
            case 0x7:               # 7xnn add value to register vx
                registers[n2] += nn
            case 0xa:               # annn set index register I
                index = nnn
            case 0xd:               # dxyn draw
                x = registers[n2]
                y = registers[n3]
                sprite = ram[index:index+n4]
                display.update_screen(x, y, sprite)
            case _:
                raise NotImplementedError(f"Instruction not implemented: {n1:X}")

        display.render_screen()

    sdl2.ext.quit()


if __name__ == "__main__":
    main()


#### TODO: Implement PC