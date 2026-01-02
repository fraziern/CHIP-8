import pygame

class Beeper():

    def __init__(self,sound_file:str):
        pygame.mixer.init()
        self.beep = pygame.mixer.Sound(sound_file)

    def play(self):
        self.beep.play(10) # loop 10x
    
    def stop(self):
        self.beep.stop()
