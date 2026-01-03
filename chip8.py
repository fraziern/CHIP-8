import time
import random
import pygame
from PygameDisplay import Display
from State import State
from Beeper import Beeper
from Keyboard import Keyboard
from debug_utils import get_instr_definition

DEBUG = False

rom_filename = r'C:\Users\Nick\source\repos\chip8\roms\6-keypad.ch8'
font_filename = r'C:\Users\Nick\source\repos\chip8\roms\font.ch8'
beep_filename = r'C:\Users\Nick\source\repos\chip8\beep-09.wav'

SIXTYHZ = 1/60  # Timer interval in seconds (approx 0.01667 seconds)
NINETIES_SHIFT = True # use the CHIP-48 version of bit shift
NINETIES_BNNN = True # use CHIP-48 version of jump with offset
IPS = 700 # Instructions per second


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


def add(state, a, b, result_to=None):
    if result_to is None:
        result_to = a
    value = state.get_vx(a) + state.get_vx(b)
    value, vf = (value % 256, 1) if value > 255 else (value, 0)
    state.set_vx(result_to,value)
    state.set_vx(0xf,vf) # carry


def subtract(state, a, b, result_to=None): 
    # function for 8xy5 and 8xy7, subtracts a - b and updates state
    if result_to is None:
        result_to = a
    value = state.get_vx(a) - state.get_vx(b)
    value, vf = ((value + 256) % 256, 0) if value < 0 else (value, 1)
    state.set_vx(result_to,value)
    state.set_vx(0xf, vf)


def right_shift(state, a, b, result_to=None):
    # 8xy6
    if result_to is None:
        result_to = a
    if NINETIES_SHIFT:
        state.set_vx(a, state.get_vx(b))
    vf = state.get_vx(a) & 0x1 # grab the rightmost bit
    state.set_vx(a, state.get_vx(a) >> 1)
    state.set_vx(0xf, vf)


def left_shift(state, a, b, result_to=None):
    # 8xye
    if result_to is None:
        result_to = a
    if NINETIES_SHIFT:
        state.set_vx(a, state.get_vx(b))
    vf = (state.get_vx(a) >> 7) & 0x1 # grab the leftmost bit
    state.set_vx(a, state.get_vx(a) << 1)
    state.set_vx(0xf, vf)


def draw_instr(state, display, vx, vy, n):
    x = state.get_vx(vx)
    y = state.get_vx(vy)
    sprite = state.get_ram(n)
    vf = display.update_screen(x, y, sprite)
    state.set_vx(0xf, vf)


def main():
    
    ROMSTART = 0x200
    FONTSTART = 0x50

    state = State()
    display = Display()
    beeper = Beeper(beep_filename)
    keyboard = Keyboard()

    #####################################################
    ### load the font rom
    with open(font_filename,'rb') as file:
        fonts = file.read()
        state.set_ram(fonts, FONTSTART)

    #####################################################
    ### load the program rom
    with open(rom_filename,'rb') as file:
        full_rom = file.read()
        state.set_ram(full_rom, ROMSTART)


    start_time = time.perf_counter()
    frame_count = 0
    clock = pygame.time.Clock()
    running = True
    if DEBUG:
        print("Press any key to advance to next frame.")

    ### MAIN LOOP
    while(running):
    
        # 1. Check events
        # wait_for_input = True
        
        # # Wait for keypress before executing frame (if in debug mode)
        # while wait_for_input:
        #     events = keyboard.get_events()
        #     if events['quit']:
        #             running = False
        #             wait_for_input = False
        #     elif events['keydown']:
        #         wait_for_input = False  # Advance to next frame
        #     elif not DEBUG:
        #         wait_for_input = False
        keyboard.get_state()
        if (keyboard.request_quit):
            running = False
        # TODO fix debug mode

        clock.tick(IPS)
        screen_updated = False  # only update screen if needed

        # 2. Manage timers
        current_time = time.perf_counter()
        elapsed_time = current_time - start_time
        if elapsed_time >= SIXTYHZ:
            start_time = current_time
            state.decrement_delay_timer()
            sound_tx_value = state.decrement_sound_timer()
            if sound_tx_value > 0:
                beeper.play()
            else:
                beeper.stop()

        # 3. Fetch instruction
        instr = state.get_ram_at_pc()
        frame_count += 1
        state.increment_pc()
        
        # 4. Decode/Execute instruction
        n1, n2, n3, n4, nn, nnn = decode_instruction(instr)
        if DEBUG:
            definition = get_instr_definition(n1, n2, n3, n4, nn, nnn)
            print(f'Instruction {state.get_pc()-ROMSTART:X}: {instr.hex()} {definition}')

        match n1:
            case 0x0:
                match nn:
                    case 0xe0:      # 00e0 clear screen
                        display.clear_screen()
                        screen_updated = True
                    case 0xee:      # 00ee return from subroutine
                        state.set_pc(state.stack_pop())
                    case _:
                        raise SyntaxError(f"Instruction not recognized: {instr.hex()}")
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
                    case 0x0:       # 8xy0 set x = y
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
                    case 0x4:       # 8xy4 add with carry
                        add(state, n2, n3, result_to=n2)
                    case 0x5:       # 8XY5 sets VX to the result of VX - VY
                        subtract(state,n2,n3)
                    case 0x6:       # 8xy6 right shift
                        right_shift(state, n2, n3)
                    case 0x7:       # 8XY7 sets VX to the result of VY - VX
                        subtract(state, n3, n2, result_to=n2)
                    case 0xe:       # 8xye left shift
                        left_shift(state, n2, n3)
                    case _:
                        raise SyntaxError(f"Instruction not recognized: {instr.hex()}")              
            case 0x9:               # 9xy0 skips if the values in VX and VY are not equal
                if state.get_vx(n2) != state.get_vx(n3):
                    state.increment_pc()
            case 0xa:               # annn set index register I
                state.set_index(nnn)
            case 0xb:               # bnnn jump with offset
                if NINETIES_BNNN:
                    state.set_pc(nnn+state.get_vx(n2))
                else:
                    state.set_pc(nnn)
            case 0xc:               # cxnn random
                r = random.randint(0,0xff)
                state.set_vx(n2,(nn & r))
            case 0xd:               # dxyn draw
                draw_instr(state, display, n2, n3, n4)
                screen_updated = True
            case 0xe:
                match nn:
                    case 0x9e:      # ex9e skip if vx key pressed
                        if keyboard.is_pressed(state.get_vx(n2)):
                            state.increment_pc()
                    case 0xa1:      # exa1 skip if vx key not pressed
                        if not keyboard.is_pressed(state.get_vx(n2)):
                            state.increment_pc()
                    case _:
                        raise SyntaxError(f"Instruction not recognized: {instr.hex()}")
            case 0xf:
                match nn:
                    case 0x07:      # fx07 get delay timer
                        state.set_vx(n2, state.get_delay_timer())
                    case 0x0a:      # fx0a get key
                        keypress = keyboard.is_pressed()
                        if not keypress:
                            state.decrement_pc()
                        else:
                            state.set_vx(n2, keypress)
                    case 0x15:      # fx15 set delay timer to vx
                        state.set_delay_timer(state.get_vx(n2))
                    case 0x18:      # fx18 set sound timer to vx
                        state.set_sound_timer(state.get_vx(n2)) 
                    case 0x1e:      # fx1e add to index
                        value = state.get_index() + state.get_vx(n2)
                        state.set_index(value, set_overflow=True)
                    case 0x29:      # fx29 set I to font location for char x
                        state.set_index((state.get_vx(n2) * 5) + FONTSTART)
                    case 0x33:      # fx33 BCD conversion
                        bcd = state.get_vx(n2)
                        bcd_list = [(bcd//100),(bcd%100)//10,bcd%10]
                        state.set_ram(bcd_list)
                    case 0x55:      # fx55 store registers to memory
                        for i in range(n2+1):
                            state.set_ram(state.get_vx(i), state.get_index()+i)
                    case 0x65:      # fx65 load registers from memory
                        for i in range(n2+1):
                            state.set_vx(i, state.get_ram(address=state.get_index()+i))
                    case _:
                        raise SyntaxError(f"Instruction not recognized: {instr.hex()}")

        # 5. Update display
        if screen_updated:
            display.render_screen()
        
        if(DEBUG):
            print(state)

    display.quit()


if __name__ == "__main__":
    main()
