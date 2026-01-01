import sys
import time
import sdl2.ext
from Display import Display

rom_filename = 'bc_test.ch8'
font_filename = 'font.ch8'

SIXTYHZ = 1/60  # Target interval in seconds (approx 0.01667 seconds)
NINETIES_SHIFT = False # use the CHIP-48 version of bit shifting

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
    delay_timer = 0
    sound_timer = 0
    ram = bytearray(4096)
    display = Display()


    #####################################################
    ### load the test rom
    with open(rom_filename,'rb') as file:
        full_rom = file.read()
        ram[ROMSTART:ROMSTART + len(full_rom)] = full_rom


    ### MAIN LOOP
    start_time = time.perf_counter()
    running = True
    while(running):
        # 1. Check events
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
        sdl2.SDL_Delay(10)

        # 2. Manage timers
        current_time = time.perf_counter()
        elapsed_time = current_time - start_time
        if elapsed_time >= SIXTYHZ:
            start_time = current_time
            delay_timer = delay_timer - 1 if delay_timer > 0 else 0
            sound_timer = sound_timer - 1 if sound_timer > 0 else 0

        # 3. Fetch instruction
        instr = ram[pc:pc+2]
        pc += 2
        
        # 4. Decode/Execute instruction
        n1, n2, n3, n4, nn, nnn = decode_instruction(instr)
        match n1:
            case 0x0:
                if nnn == 0x0e0:    # 00e0 clear screen
                    display.clear_screen()
            case 0x1:               # 1nnn jump
                pc = nnn
            case 0x3:               # 3xnn skip one instr if vx == nn
                if registers[n2] == nn:
                    pc += 2
            case 0x4:               # 4xnn skip one instr if vx != nn
                if registers[n2] != nn:
                    pc += 2
            case 0x5:               # 5xy0 skips if the values in VX and VY are equal
                if registers[n2] == registers[n3]:
                    pc += 2
            case 0x6:               # 6xnn set register vx
                registers[n2] = nn
            case 0x7:               # 7xnn add value to register vx
                registers[n2] += nn
            case 0x8:
                match n4:
                    case 0x0:       # 8xy0 set
                        registers[n2] = registers[n3]
                    case 0x1:       # 8xy1 binary OR
                        registers[n2] = registers[n2] | registers[n3]
                    case 0x2:       # 8xy2 binary AND
                        registers[n2] = registers[n2] & registers[n3]
                    case 0x3:       # 8xy3 binary XOR
                        registers[n2] = registers[n2] ^ registers[n3]
                    case 0x4:       # 8xy4 add
                        registers[n2] = registers[n2] + registers[n3]
                    case 0x5:       # 8XY5 sets VX to the result of VX - VY
                        registers[0xf] = 1 if registers[n2] > registers[n3] else 0
                        registers[n2] = abs(registers[n2] - registers[n3])
                    case 0x7:       # 8XY7 sets VX to the result of VY - VX
                        registers[0xf] = 1 if registers[n3] > registers[n2] else 0
                        registers[n2] = abs(registers[n3] - registers[n2])
                    case 0x6:       # 8xy6 right shift
                        if NINETIES_SHIFT:
                            registers[n2] = registers[n3]
                        registers[0xf] = n2 & 0x1 # grab the rightmost bit
                        registers[n2] = registers[n2] >> 1
                    case 0xe:       # 8xye left shift
                        if NINETIES_SHIFT:
                            registers[n2] = registers[n3]
                        registers[0xf] = (n2 >> 7) & 0x1 # grab the leftmost bit
                        registers[n2] = registers[n2] << 1                       
            case 0x9:               # 9xy0 skips if the values in VX and VY are not equal
                if registers[n2] != registers[n3]:
                    pc += 2
            case 0xa:               # annn set index register I
                index = nnn
            case 0xd:               # dxyn draw
                x = registers[n2]
                y = registers[n3]
                sprite = ram[index:index+n4]
                display.update_screen(x, y, sprite)
                # TODO set vf
            case 0xf:
                match nn:
                    case 0x29:
                        raise NotImplementedError(f"Instruction not implemented: fonts")
                    case _:
                        raise NotImplementedError(f"Instruction not implemented: {instr.hex()}")
            case _:
                raise NotImplementedError(f"Instruction not implemented: {instr.hex()}")

        # 5. Update display
        display.render_screen() # TODO: only redraw screen when theres a display instruction

    sdl2.ext.quit()


if __name__ == "__main__":
    main()
