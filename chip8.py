import time
import random
import pygame
from PygameDisplay import Display
from State import State
from Beeper import Beeper
from Keyboard import Keyboard
from debug_utils import get_instr_definition

DEBUG = False

rom_filename = r'C:\Users\Nick\source\repos\chip8\roms\games\15 Puzzle [Roger Ivie] (alt).ch8'
font_filename = r'C:\Users\Nick\source\repos\chip8\roms\font.ch8'
beep_filename = r'C:\Users\Nick\source\repos\chip8\beep-09.wav'

SIXTYHZ = 1/60  # Timer interval in seconds (approx 0.01667 seconds)
NINETIES_SHIFT = True # use the CHIP-48 version of bit shift
NINETIES_BNNN = True # use CHIP-48 version of jump with offset
IPS = 700 # Instructions per second





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
        wait_for_input = True
        
        # Wait for keypress before executing frame (if in debug mode)
        while wait_for_input:
            events = keyboard.get_events()
            if events['quit']:
                    running = False
                    wait_for_input = False
            elif events['keydown']:
                wait_for_input = False  # Advance to next frame
            elif not DEBUG:
                wait_for_input = False

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


        # 5. Update display
        if screen_updated:
            display.render_screen()
        

    display.quit()


if __name__ == "__main__":
    main()
