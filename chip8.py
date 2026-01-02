import time
import sdl2
import sdl2.ext
from sdl2.ext import input
from Display import Display
from State import State
from Beeper import Beeper

DEBUG = False

rom_filename = r'C:\Users\Nick\source\repos\chip8\roms\6-keypad.ch8'
font_filename = r'C:\Users\Nick\source\repos\chip8\roms\font.ch8'
beep_filename = r'C:\Users\Nick\source\repos\chip8\beep-09.wav'

SIXTYHZ = 1/60  # Timer interval in seconds (approx 0.01667 seconds)
NINETIES_SHIFT = False # use the CHIP-48 version of bit 

keys = { 0:sdl2.SDL_SCANCODE_X,
    1:sdl2.SDL_SCANCODE_1,
    2:sdl2.SDL_SCANCODE_2,
    3:sdl2.SDL_SCANCODE_3,
    4:sdl2.SDL_SCANCODE_Q,
    5:sdl2.SDL_SCANCODE_W,
    6:sdl2.SDL_SCANCODE_E,
    7:sdl2.SDL_SCANCODE_A,
    8:sdl2.SDL_SCANCODE_S,
    9:sdl2.SDL_SCANCODE_D,
    0xb:sdl2.SDL_SCANCODE_C,
    0xa:sdl2.SDL_SCANCODE_Z,
    0xc:sdl2.SDL_SCANCODE_4,
    0xd:sdl2.SDL_SCANCODE_R,
    0xe:sdl2.SDL_SCANCODE_F,
    0xf:sdl2.SDL_SCANCODE_V,
    }

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


def update_key_state(events, state:State):

    
    for key in keys:
        if input.key_pressed(events, keys[key]):
            state.set_key_state(key,True)
        else:
            state.set_key_state(key,False)


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
    beeper = Beeper(beep_filename)
    keyboard_state = sdl2.SDL_GetKeyboardState(None)
    # keyboard = Keyboard()

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


    ### MAIN LOOP
    start_time = time.perf_counter()
    frame_count = 0
    running = True
    if DEBUG:
        print("Press any key to advance to next frame.")

    while(running):
    
        # 1. Check events
        wait_for_input = True
        
        # # Wait for keypress before executing frame
        # while wait_for_input:
        #     events = sdl2.ext.get_events()
        #     if not events and not DEBUG:
        #         wait_for_input = False
        #     for event in events:
        #         if event.type == sdl2.SDL_QUIT:
        #             running = False
        #             wait_for_input = False
        #         elif event.type == sdl2.SDL_KEYDOWN:
        #             wait_for_input = False  # Advance to next frame
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
        # update_key_state(events, state)

        # sdl2.SDL_Delay(5)
        screen_updated = False

        # 2. Manage timers
        current_time = time.perf_counter()
        elapsed_time = current_time - start_time
        if elapsed_time >= SIXTYHZ:
            start_time = current_time
            delay_tx_value = state.decrement_delay_timer()
            sound_tx_value = state.decrement_sound_timer()
            if sound_tx_value > 0:
                beeper.play()
            else:
                beeper.stop()

        # 3. Fetch instruction
        instr = state.get_ram_at_pc()
        frame_count += 1
        if DEBUG:
            print(f'Instruction {state.get_pc()-ROMSTART:X}: {instr.hex()}')
        state.increment_pc()
        
        # 4. Decode/Execute instruction
        n1, n2, n3, n4, nn, nnn = decode_instruction(instr)
        match n1:
            case 0x0:
                match nn:
                    case 0xe0:      # 00e0 clear screen
                        display.clear_screen()
                        screen_updated = True
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
                    case 0x4:       # 8xy4 add
                        value = state.get_vx(n2) + state.get_vx(n3)
                        state.set_vx(n2,value)
                    case 0x5:       # 8XY5 sets VX to the result of VX - VY
                        state.set_vx(n2,subtract(state,n2,n3))
                    case 0x6:       # 8xy6 right shift
                        if NINETIES_SHIFT:
                            state.set_vx(n2, state.get_vx(n3))
                        state.set_vx(0xf,(state.get_vx(n2) & 0x1)) # grab the rightmost bit
                        state.set_vx(n2, state.get_vx(n2) >> 1)
                    case 0x7:       # 8XY7 sets VX to the result of VY - VX
                        state.set_vx(n2,subtract(state,n3,n2))
                    case 0xe:       # 8xye left shift
                        if NINETIES_SHIFT:
                            state.set_vx(n2, state.get_vx(n3))
                        state.set_vx(0xf,((state.get_vx(n2) >> 7) & 0x1)) # grab the leftmost bit
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
                screen_updated = True
                # TODO set vf
            case 0xe:
                match nn:
                    case 0x9e:      # ex9e skip if vx key pressed
                        key_to_check = keys[state.get_vx(n2) & 0x1]
                        if keyboard_state[key_to_check]:
                            state.increment_pc()
                    case 0xa1:      # exa1 skip if vx key not pressed
                        key_to_check = keys[state.get_vx(n2) & 0x1]
                        if not keyboard_state[key_to_check]:
                            state.increment_pc()
            case 0xf:
                match nn:
                    case 0x07:      # fx07 get delay timer
                        state.set_vx(n2, state.get_delay_timer())
                    case 0x15:      # fx15 set delay timer to vx
                        state.set_delay_timer(state.get_vx(n2))
                    case 0x18:      # fx18 set sound timer to vx
                        state.set_sound_timer(state.get_vx(n2)) 
                    case 0x1e:      # fx1e add to index
                        value = state.get_index() + state.get_vx(n2)
                        state.set_index(value, set_overflow=True)
                    case 0x29:      # fx29 set I to font location for char x
                        state.set_index((n2 * 5) + FONTSTART)
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
                        raise NotImplementedError(f"Instruction not implemented: {instr.hex()}")
            case _:
                raise NotImplementedError(f"Instruction not implemented: {instr.hex()}")

        # 5. Update display
        if screen_updated:
            display.render_screen() # TODO: only redraw screen when theres a display instruction

    sdl2.ext.quit()


if __name__ == "__main__":
    main()
