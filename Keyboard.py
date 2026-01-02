# import sdl2.ext
import pygame

class Keyboard():

    keys = { 0:pygame.K_x,
        1:pygame.K_1,
        2:pygame.K_2,
        3:pygame.K_3,
        4:pygame.K_q,
        5:pygame.K_w,
        6:pygame.K_e,
        7:pygame.K_a,
        8:pygame.K_s,
        9:pygame.K_d,
        0xa:pygame.K_z,
        0xb:pygame.K_c,
        0xc:pygame.K_4,
        0xd:pygame.K_r,
        0xe:pygame.K_f,
        0xf:pygame.K_v,
        }

    def __init__(self):
        pygame.init()
    

    def get_events(self):
        actions = {'quit':False,'keydown':False}

        for event in pygame.event.get():
            # Check for Window Close (X button)
            if event.type == pygame.QUIT:
                actions['quit'] = True
                
            # Check for  Key Press
            if event.type == pygame.KEYDOWN and event.key in self.keys.values():
                found_key = next((key for key, value in self.keys.items() if value == event.key), None)
                actions[found_key] = True
                actions['keydown'] = True
                    
        return actions
    
    
    def is_pressed(self, key_hex:int = None):

        #1. individual actions
        if key_hex is None:
            for event in pygame.event.get():
                if event.type == pygame.KEYUP and event.key in self.keys.values():
                    found_key = next((key for key, value in self.keys.items() if value == event.key), None)
                    return found_key
            return False
        
        #2. Held down
        key_to_check = self.keys[key_hex & 0xf] # mask to limit value to 0-f
        keys_pressed = pygame.key.get_pressed()
        return keys_pressed[key_to_check]
