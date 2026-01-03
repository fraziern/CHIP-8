# import sdl2.ext
import pygame

class Keyboard():

    keytable = { pygame.K_x:0,
        pygame.K_1:1,
        pygame.K_2:2,
        pygame.K_3:3,
        pygame.K_q:4,
        pygame.K_w:5,
        pygame.K_e:6,
        pygame.K_a:7,
        pygame.K_s:8,
        pygame.K_d:9,
        pygame.K_z:0xa,
        pygame.K_c:0xb,
        pygame.K_4:0xc,
        pygame.K_r:0xd,
        pygame.K_f:0xe,
        pygame.K_v:0xf,
        }


    def __init__(self):
        pygame.init()
        # current_state and previous_state hold true/false for each key (16 total)
        self.previous_state = [False] * 16
        self.current_state = [False] * 16
        self.request_quit = False
    

    # def get_events(self):
    #     actions = {'quit':False,'keydown':False}

    #     for event in pygame.event.get():
    #         print(event)
    #         # Check for Window Close (X button)
    #         if event.type == pygame.QUIT:
    #             actions['quit'] = True
                
    #         # Check for  Key Press
    #         if event.type == pygame.KEYDOWN and event.key in self.keytable.keys():
    #             found_key = self.keytable[event.key]
    #             actions[found_key] = True
    #             actions['keydown'] = True
                    
    #     return actions
    

    def get_state(self):
        # print(self.current_state, end="\r", flush=True)
        self.previous_state = self.current_state.copy()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.request_quit = True
            elif event.type == pygame.KEYDOWN and event.key in self.keytable:
                self.current_state[self.keytable[event.key]] = True
            elif event.type == pygame.KEYUP and event.key in self.keytable:
                self.current_state[self.keytable[event.key]] = False
        
    
    def is_pressed(self, key_hex:int = None):
        # this does not get new events, but only checks current/previous state

        #1. individual actions
        if key_hex is None:
            for keyvalue in range(16):
                if self.previous_state[keyvalue] and not self.current_state[keyvalue]: # key up event
                    return keyvalue
            return False
        
        #2. Held down
        key_to_check = key_hex & 0xf # mask to limit value to 0-f
        return self.current_state[key_to_check]
