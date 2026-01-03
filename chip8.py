import time
import pygame
from PygameDisplay import Display
from State import State
from Beeper import Beeper
from Keyboard import Keyboard
from CPU import CPU

DEBUG = False

rom_filename = r'C:\Users\Nick\source\repos\chip8\roms\games\Breakout [Carmelo Cortez, 1979].ch8'
font_filename = r'C:\Users\Nick\source\repos\chip8\roms\font.ch8'
beep_filename = r'C:\Users\Nick\source\repos\chip8\beep-09.wav'

SIXTYHZ = 1/60  # Timer interval in seconds (approx 0.01667 seconds)
config = { 'nineties_shift':False, # use the CHIP-48 version of bit shift
          'nineties_bnnn':False, # use CHIP-48 version of jump with offset
          'debug':False,
          }
FPS = 60 # Frames per second
CYCLES_PER_FRAME = 15


def main():

    pygame.init()

    state = State()
    display = Display()
    beeper = Beeper(beep_filename)
    keyboard = Keyboard()
    cpu = CPU(state, keyboard, display, config)

    ROMSTART = cpu.ROMSTART
    FONTSTART = cpu.FONTSTART

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

        # 2. Manage timers
        state.decrement_delay_timer()
        sound_tx_value = state.decrement_sound_timer()
        if sound_tx_value > 0:
            beeper.play()
        else:
            beeper.stop()

        # 3. cpu cycle
        for _ in range(CYCLES_PER_FRAME):
            cpu.run_cycle()

        # 4. Update display
        display.render_screen()

        # 5. sleep until FPS met
        clock.tick(FPS)
        

    display.quit()


if __name__ == "__main__":
    main()
