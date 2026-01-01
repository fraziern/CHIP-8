import sys
import time
import math
import sdl2.ext
from Display import Display
from State import State

DEBUG = False

rom_filename = r'C:\Users\Nick\source\repos\chip8\roms\3-corax.ch8'
font_filename = r'C:\Users\Nick\source\repos\chip8\roms\font.ch8'

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


def subtract(state, a, b): 
    # function for 8xy5 and 8xy7, subtracts a - b and updates state,
    # returns value. does NOT set vx
    carry = 1
    value = state.get_vx(a) - state.get_vx(b)
    if value < 0:  # emulate underflow
        carry = 0
        value = (value + 256) % 256
    state.set_vx(0xf,carry)
    return value

    
def main():
    
    ROMSTART = 0x200
    FONTSTART = 0x50

    state = State()
    display = Display()


    #####################################################
    ### load the font rom
    with open(font_filename,'rb') as file:
        fonts = file.read()
        state.set_ram(fonts, FONTSTART)

    #####################################################
    ### load the test rom
    with open(rom_filename,'rb') as file:
        full_rom = file.read()
        state.set_ram(full_rom, ROMSTART)


    ### MAIN LOOP
    start_time = time.perf_counter()
    running = True
    while(running):
        # 1. Check events
        if DEBUG:
            print("Press any key to advance to next frame.")
        wait_for_input = True
        
        # Wait for keypress before executing frame
        while wait_for_input:
            events = sdl2.ext.get_events()
            if not events and not DEBUG:
                wait_for_input = False
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    running = False
                    wait_for_input = False
                elif event.type == sdl2.SDL_KEYDOWN:
                    wait_for_input = False  # Advance to next frame

        sdl2.SDL_Delay(10)

        # 2. Manage timers
        current_time = time.perf_counter()
        elapsed_time = current_time - start_time
        if elapsed_time >= SIXTYHZ:
            start_time = current_time
            state.decrement_delay_timer()
            state.decrement_sound_timer()

        # 3. Fetch instruction
        instr = state.get_ram_at_pc()
        if DEBUG:
            print(f'Instruction: {instr.hex()}')
        state.increment_pc()
        
        # 4. Decode/Execute instruction
        n1, n2, n3, n4, nn, nnn = decode_instruction(instr)
        match n1:
            case 0x0:
                match nn:
                    case 0xe0:      # 00e0 clear screen
                        display.clear_screen()
                    case 0xee:      # 00ee return from subroutine
                        state.set_pc(state.stack_pop())
            case 0x1:               # 1nnn jump
                state.set_pc(nnn)
            case 0x2:               # 2nnn call subroutine
                state.stack_push(state.get_pc())
                state.set_pc(nnn)
            case 0x3:               # 3xnn skip one instr if vx == nn
                if state.get_vx(n2) == nn:
                    state.increment_pc()
            case 0x4:               # 4xnn skip one instr if vx != nn
                if state.get_vx(n2) != nn:
                    state.increment_pc()
            case 0x5:               # 5xy0 skips if the values in VX and VY are equal
                if state.get_vx(n2) == state.get_vx(n3):
                    state.increment_pc()
            case 0x6:               # 6xnn set register vx
                state.set_vx(n2, nn)
            case 0x7:               # 7xnn add value to register vx
                new_value = state.get_vx(n2) + nn
                state.set_vx(n2, new_value)
            case 0x8:
                match n4:
                    case 0x0:       # 8xy0 set
                        state.set_vx(n2,state.get_vx(n3))
                    case 0x1:       # 8xy1 binary OR
                        value = state.get_vx(n2) | state.get_vx(n3)
                        state.set_vx(n2,value)
                    case 0x2:       # 8xy2 binary AND
                        value = state.get_vx(n2) & state.get_vx(n3)
                        state.set_vx(n2,value)
                    case 0x3:       # 8xy3 binary XOR
                        value = state.get_vx(n2) ^ state.get_vx(n3)
                        state.set_vx(n2,value)
                    case 0x4:       # 8xy4 add
                        value = state.get_vx(n2) + state.get_vx(n3)
                        state.set_vx(n2,value)
                    case 0x5:       # 8XY5 sets VX to the result of VX - VY
                        state.set_vx(n2,subtract(state,n2,n3))
                    case 0x7:       # 8XY7 sets VX to the result of VY - VX
                        state.set_vx(n2,subtract(state,n3,n2))
                    case 0x6:       # 8xy6 right shift
                        if NINETIES_SHIFT:
                            state.set_vx(n2, state.get_vx(n3))
                        state.set_vx(0xf,(n2 & 0x1)) # grab the rightmost bit
                        state.set_vx(n2, state.get_vx(n2) >> 1)
                    case 0xe:       # 8xye left shift
                        if NINETIES_SHIFT:
                            state.set_vx(n2, state.get_vx(n3))
                        state.set_vx(0xf,((n2 >> 7) & 0x1)) # grab the leftmost bit
                        state.set_vx(n2, state.get_vx(n2) << 1)                  
            case 0x9:               # 9xy0 skips if the values in VX and VY are not equal
                if state.get_vx(n2) != state.get_vx(n3):
                    state.increment_pc()
            case 0xa:               # annn set index register I
                state.set_index(nnn)
            case 0xd:               # dxyn draw
                x = state.get_vx(n2)
                y = state.get_vx(n3)
                sprite = state.get_ram(n4)
                display.update_screen(x, y, sprite)
                # TODO set vf
            case 0xf:
                match nn:
                    case 0x29:      # fx29 set I to font location for char x
                        state.set_index((n2 * 5) + FONTSTART)
                    case 0x33:      # fx33 BCD conversion
                        number1 = math.floor(nnn / 100)
                        number2 = math.floor((nnn - number1*100) / 10)
                        number3 = nnn - number1*100 - number2*10
                        state.set_ram([number1, number2, number3])
                    case 0x55:      # fx55 store registers to memory
                        for i in range(n2+1):
                            state.set_ram(state.get_vx(i), state.get_index()+i)
                    case 0x65:      # fx65 load registers from memory
                        for i in range(n2+1):
                            state.set_vx(i, state.get_ram(address=state.get_index()+i))
                    case 0x1e:      # fx1e add to index
                        state.set_index(n2, set_overflow=True)
                    case _:
                        raise NotImplementedError(f"Instruction not implemented: {instr.hex()}")
            case _:
                raise NotImplementedError(f"Instruction not implemented: {instr.hex()}")

        # 5. Update display
        display.render_screen() # TODO: only redraw screen when theres a display instruction

    sdl2.ext.quit()


if __name__ == "__main__":
    main()
