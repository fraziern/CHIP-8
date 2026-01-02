from sdl2.ext import input
import sdl2.ext

class Keyboard():

    keys = { 0:'x',
            1:'1',
            2:'2',
            3:'3',
            4:'q',
            5:'w',
            6:'e',
            7:'a',
            8:'s',
            9:'d',
            0xb:'c',
            0xa:'z',
            0xc:'4',
            0xd:'r',
            0xe:'f',
            0xf:'v',
            }

    def __init__(self):
        sdl2.ext.init()
        self.events = None
    
    def is_pressed(self, events, key:int):
        return input.key_pressed(events, self.keys[key])
